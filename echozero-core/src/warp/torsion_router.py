"""
Torsion Router - Phase-based Attention Routing

Implements torsion-based routing using trefoil phase relationships.
Modulates attention weights based on phase coherence/mismatch.

Torsion represents "twist" in the geometric structure:
- Low torsion: Phase-aligned paths (high coherence)
- High torsion: Phase-mismatched paths (suppressed)
"""

import torch
import numpy as np
from typing import Tuple, Optional


def trefoil_phase(t: torch.Tensor) -> torch.Tensor:
    """
    Compute trefoil knot phase embedding

    Maps scalar parameters to 3-fold symmetric phases via sin(3t).
    This creates topological structure isomorphic to trefoil knot.

    Args:
        t: Parameter tensor [N] or [batch, N]

    Returns:
        Trefoil phases [N] or [batch, N], bounded in [-1, 1]
    """
    return torch.sin(3 * t)


def torsion_loss(
    phases_i: torch.Tensor,
    phases_j: torch.Tensor,
    scale: float = 0.1,
    mode: str = 'l1'
) -> torch.Tensor:
    """
    Compute torsion penalty from phase mismatch

    Quantifies the "twist" required to align phase_i with phase_j.
    Higher mismatch → higher torsion → lower attention.

    Args:
        phases_i: Source phases [batch, num_nodes, dim] or [num_nodes, dim]
        phases_j: Target phases [batch, num_nodes, dim] or [num_nodes, dim]
        scale: Torsion scaling factor
        mode: Mismatch metric - 'l1', 'l2', or 'cosine'

    Returns:
        Torsion penalties [batch, num_nodes, num_nodes] or [num_nodes, num_nodes]
    """
    # Handle unbatched input
    if phases_i.dim() == 2:
        phases_i = phases_i.unsqueeze(0)
        phases_j = phases_j.unsqueeze(0)
        unbatch = True
    else:
        unbatch = False

    batch_size, num_nodes, dim = phases_i.shape

    # Expand for pairwise comparison
    # [batch, num_nodes, 1, dim] vs [batch, 1, num_nodes, dim]
    phases_i_exp = phases_i.unsqueeze(2)  # [batch, num_nodes, 1, dim]
    phases_j_exp = phases_j.unsqueeze(1)  # [batch, 1, num_nodes, dim]

    # Compute mismatch based on mode
    if mode == 'l1':
        # L1 distance - absolute phase difference
        mismatch = torch.abs(phases_i_exp - phases_j_exp).mean(dim=-1)

    elif mode == 'l2':
        # L2 distance - Euclidean phase difference
        mismatch = torch.norm(phases_i_exp - phases_j_exp, p=2, dim=-1) / np.sqrt(dim)

    elif mode == 'cosine':
        # Cosine distance - angular phase difference
        # 1 - cosine_similarity, bounded [0, 2]
        cosine_sim = torch.nn.functional.cosine_similarity(
            phases_i_exp,
            phases_j_exp,
            dim=-1
        )
        mismatch = 1 - cosine_sim

    else:
        raise ValueError(f"Unknown mode: {mode}. Use 'l1', 'l2', or 'cosine'")

    # Scale mismatch to torsion penalty
    torsion = scale * mismatch

    # Remove batch dimension if input was unbatched
    if unbatch:
        torsion = torsion.squeeze(0)

    return torsion


def coherence_score(
    phases: torch.Tensor,
    metric: str = 'std'
) -> torch.Tensor:
    """
    Compute phase coherence across nodes

    Measures how aligned/synchronized the phases are.
    Lower variance → higher coherence → better signal funneling.

    Args:
        phases: Phase tensor [batch, num_nodes, dim] or [num_nodes, dim]
        metric: Coherence metric - 'std', 'entropy', or 'iqr'

    Returns:
        Coherence scores [batch] or scalar
    """
    if metric == 'std':
        # Standard deviation (lower = more coherent)
        if phases.dim() == 3:
            coherence = phases.std(dim=(1, 2))  # [batch]
        else:
            coherence = phases.std()  # scalar
        # Invert so higher = more coherent
        coherence = 1.0 / (1.0 + coherence)

    elif metric == 'entropy':
        # Phase entropy (lower = more coherent)
        # Discretize phases into bins
        bins = 20
        if phases.dim() == 3:
            batch_size = phases.shape[0]
            entropies = []
            for b in range(batch_size):
                hist = torch.histc(phases[b].flatten(), bins=bins, min=-1, max=1)
                hist = hist / (hist.sum() + 1e-8)  # Normalize
                entropy = -(hist * torch.log(hist + 1e-8)).sum()
                entropies.append(entropy)
            coherence = torch.stack(entropies)
        else:
            hist = torch.histc(phases.flatten(), bins=bins, min=-1, max=1)
            hist = hist / (hist.sum() + 1e-8)
            coherence = -(hist * torch.log(hist + 1e-8)).sum()
        # Invert
        coherence = 1.0 / (1.0 + coherence)

    elif metric == 'iqr':
        # Interquartile range (lower = more coherent)
        if phases.dim() == 3:
            q75 = torch.quantile(phases, 0.75, dim=(1, 2))
            q25 = torch.quantile(phases, 0.25, dim=(1, 2))
        else:
            q75 = torch.quantile(phases, 0.75)
            q25 = torch.quantile(phases, 0.25)
        iqr = q75 - q25
        coherence = 1.0 / (1.0 + iqr)

    else:
        raise ValueError(f"Unknown metric: {metric}")

    return coherence


def phase_synchronization(
    phases_i: torch.Tensor,
    phases_j: torch.Tensor,
    threshold: float = 0.5
) -> Tuple[torch.Tensor, torch.Tensor]:
    """
    Identify phase-synchronized node pairs

    Finds pairs where phases are aligned (low torsion).
    Useful for identifying resonant pathways.

    Args:
        phases_i: Source phases [num_nodes, dim]
        phases_j: Target phases [num_nodes, dim]
        threshold: Synchronization threshold (lower = stricter)

    Returns:
        Tuple of:
            - sync_mask: Boolean mask [num_nodes, num_nodes] of synchronized pairs
            - sync_strength: Synchronization strength [num_nodes, num_nodes]
    """
    # Compute phase similarity (inverse of mismatch)
    mismatch = torch.abs(phases_i.unsqueeze(1) - phases_j.unsqueeze(0)).mean(dim=-1)
    sync_strength = 1.0 - mismatch  # Bounded [0, 1]

    # Threshold for binary mask
    sync_mask = sync_strength > threshold

    return sync_mask, sync_strength


def torsion_regularizer(
    torsion: torch.Tensor,
    target: float = 0.1,
    mode: str = 'l2'
) -> torch.Tensor:
    """
    Regularization loss to control torsion magnitude

    Encourages torsion to stay near target value for stability.

    Args:
        torsion: Torsion tensor [batch, num_nodes, num_nodes]
        target: Target torsion magnitude
        mode: Loss mode - 'l1', 'l2', or 'huber'

    Returns:
        Regularization loss (scalar)
    """
    if mode == 'l1':
        loss = torch.abs(torsion - target).mean()
    elif mode == 'l2':
        loss = ((torsion - target) ** 2).mean()
    elif mode == 'huber':
        # Huber loss - robust to outliers
        delta = 1.0
        diff = torch.abs(torsion - target)
        loss = torch.where(
            diff < delta,
            0.5 * diff ** 2,
            delta * (diff - 0.5 * delta)
        ).mean()
    else:
        raise ValueError(f"Unknown mode: {mode}")

    return loss


def visualize_torsion_field(
    positions: torch.Tensor,
    phases: torch.Tensor,
    save_path: Optional[str] = None
):
    """
    Visualize torsion field over node positions

    Creates a quiver plot showing phase gradients (torsion directions).

    Args:
        positions: Node positions [num_nodes, 3]
        phases: Node phases [num_nodes, dim]
        save_path: Optional path to save figure
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not available for visualization")
        return

    pos_np = positions.cpu().numpy()
    phases_np = phases.cpu().numpy()

    # Compute average phase per node
    avg_phase = phases_np.mean(axis=1)

    # Estimate gradients via finite differences
    gradients_x = []
    gradients_y = []

    for i in range(len(pos_np)):
        # Find nearest neighbors
        dists = np.linalg.norm(pos_np - pos_np[i], axis=1)
        neighbors = np.argsort(dists)[1:5]  # 4 nearest

        # Estimate gradient
        dx = pos_np[neighbors, 0] - pos_np[i, 0]
        dy = pos_np[neighbors, 1] - pos_np[i, 1]
        dphase = avg_phase[neighbors] - avg_phase[i]

        # Weighted average
        weights = 1.0 / (dists[neighbors] + 1e-8)
        grad_x = (dphase * dx * weights).sum() / weights.sum()
        grad_y = (dphase * dy * weights).sum() / weights.sum()

        gradients_x.append(grad_x)
        gradients_y.append(grad_y)

    gradients_x = np.array(gradients_x)
    gradients_y = np.array(gradients_y)

    # Plot
    plt.figure(figsize=(12, 10))
    plt.scatter(pos_np[:, 0], pos_np[:, 1], c=avg_phase, cmap='twilight',
                s=100, alpha=0.6, edgecolors='black')
    plt.quiver(pos_np[:, 0], pos_np[:, 1], gradients_x, gradients_y,
               scale=5, alpha=0.7, color='red')
    plt.colorbar(label='Average Phase')
    plt.title('Torsion Field Visualization')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.axis('equal')

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved visualization to {save_path}")
    else:
        plt.show()

    plt.close()
