"""
Ricci Affinity Computation

Computes attention affinities based on Ricci-warped distance metrics.
Implements geometric warping to create hyperbolic-like attention spaces.

The Ricci curvature parameter controls local geometry:
- Negative Ricci (< 0): Hyperbolic geometry, distances expand
- Zero Ricci (= 0): Flat Euclidean geometry
- Positive Ricci (> 0): Spherical geometry, distances contract
"""

import torch
import torch.nn.functional as F
from typing import Optional, Tuple


def ricci_affinity(
    pos: torch.Tensor,
    ricci: float = -2.0,
    temperature: float = 1.0,
    normalize: bool = True
) -> torch.Tensor:
    """
    Compute Ricci-warped attention affinities from node positions

    Implements geometric warping of distances based on Ricci curvature,
    then converts to softmax attention weights.

    Args:
        pos: Node positions [batch, num_nodes, 3] or [num_nodes, 3]
        ricci: Ricci curvature parameter (negative = hyperbolic)
        temperature: Softmax temperature (higher = more uniform)
        normalize: Whether to apply softmax normalization

    Returns:
        Affinity matrix [batch, num_nodes, num_nodes] or [num_nodes, num_nodes]
    """
    # Handle unbatched input
    if pos.dim() == 2:
        pos = pos.unsqueeze(0)  # Add batch dimension
        unbatch = True
    else:
        unbatch = False

    batch_size, num_nodes, _ = pos.shape

    # Compute pairwise positions: [batch, num_nodes, num_nodes, 3]
    pos_i = pos.unsqueeze(2).expand(batch_size, num_nodes, num_nodes, -1)
    pos_j = pos.unsqueeze(1).expand(batch_size, num_nodes, num_nodes, -1)

    # Euclidean distances: [batch, num_nodes, num_nodes]
    dist = torch.norm(pos_i - pos_j, dim=-1)

    # Warp distances based on Ricci curvature
    warped_dist = ricci_warp(dist, pos_i, pos_j, ricci)

    # Convert to affinity: exp(-ricci * warped_dist)
    # Note: ricci is typically negative, so this becomes exp(|ricci| * warped_dist)
    # which emphasizes distant nodes in hyperbolic space
    affinity = torch.exp(-torch.abs(ricci) * warped_dist / temperature)

    # Optional normalization (softmax over each row)
    if normalize:
        affinity = F.softmax(affinity, dim=-1)

    # Remove batch dimension if input was unbatched
    if unbatch:
        affinity = affinity.squeeze(0)

    return affinity


def ricci_warp(
    dist: torch.Tensor,
    pos_i: torch.Tensor,
    pos_j: torch.Tensor,
    ricci: float
) -> torch.Tensor:
    """
    Warp Euclidean distances according to Ricci curvature

    Implements a smooth warping function that modulates distances
    based on local geometry (position-dependent curvature).

    Args:
        dist: Euclidean distances [batch, num_nodes, num_nodes]
        pos_i: Source positions [batch, num_nodes, num_nodes, 3]
        pos_j: Target positions [batch, num_nodes, num_nodes, 3]
        ricci: Ricci curvature parameter

    Returns:
        Warped distances [batch, num_nodes, num_nodes]
    """
    # Compute midpoint radii (distance from origin)
    midpoint = (pos_i + pos_j) / 2
    r_mean = torch.norm(midpoint, dim=-1)

    # Warping function based on Ricci curvature
    if ricci < 0:
        # Hyperbolic warping: distances expand away from origin
        # Use sinh for smooth exponential growth
        warp_factor = torch.sinh(torch.abs(ricci) * r_mean) / (torch.abs(ricci) * r_mean + 1e-8)
    elif ricci > 0:
        # Spherical warping: distances contract
        # Use sin for periodic contraction
        warp_factor = torch.sin(ricci * r_mean) / (ricci * r_mean + 1e-8)
    else:
        # Flat (Euclidean) - no warping
        warp_factor = torch.ones_like(r_mean)

    # Apply warping to distances
    warped_dist = dist * warp_factor

    # Clamp to avoid numerical issues
    warped_dist = torch.clamp(warped_dist, min=1e-8, max=1e3)

    return warped_dist


def compute_ricci_flow(
    pos: torch.Tensor,
    ricci: float,
    dt: float = 0.1,
    steps: int = 10
) -> torch.Tensor:
    """
    Simulate Ricci flow on node positions

    Evolves positions according to Ricci flow equation:
    ∂pos/∂t = -Ricci * pos

    This can be used to optimize node positions for better geometry.

    Args:
        pos: Initial positions [num_nodes, 3]
        ricci: Ricci curvature parameter
        dt: Time step size
        steps: Number of evolution steps

    Returns:
        Evolved positions [num_nodes, 3]
    """
    pos_evolved = pos.clone()

    for _ in range(steps):
        # Compute gradient based on Ricci curvature
        # Negative Ricci → positions drift outward (expansion)
        # Positive Ricci → positions drift inward (contraction)
        gradient = -ricci * pos_evolved

        # Euler step
        pos_evolved = pos_evolved + dt * gradient

    return pos_evolved


def sectional_curvature(
    pos: torch.Tensor,
    ricci: float,
    epsilon: float = 1e-4
) -> torch.Tensor:
    """
    Estimate sectional curvature at each node

    Computes local curvature by analyzing geodesic deviation.

    Args:
        pos: Node positions [num_nodes, 3]
        ricci: Global Ricci parameter
        epsilon: Perturbation size for numerical estimation

    Returns:
        Curvature estimates [num_nodes]
    """
    num_nodes = pos.shape[0]
    curvatures = []

    for i in range(num_nodes):
        # Perturb position slightly
        pos_perturbed = pos.clone()
        pos_perturbed[i] += torch.randn(3) * epsilon

        # Compute change in distances to neighbors
        dist_original = torch.norm(pos - pos[i], dim=-1)
        dist_perturbed = torch.norm(pos - pos_perturbed[i], dim=-1)

        # Curvature estimate from geodesic deviation
        deviation = (dist_perturbed - dist_original) / epsilon
        curvature = -deviation.mean()  # Average deviation

        curvatures.append(curvature)

    return torch.tensor(curvatures)


def visualize_affinity(
    affinity: torch.Tensor,
    save_path: Optional[str] = None,
    title: str = "Ricci Affinity Matrix"
):
    """
    Visualize affinity matrix as heatmap

    Args:
        affinity: Affinity matrix [num_nodes, num_nodes]
        save_path: Optional path to save figure
        title: Plot title
    """
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("matplotlib not available for visualization")
        return

    aff_np = affinity.detach().cpu().numpy()

    plt.figure(figsize=(10, 8))
    plt.imshow(aff_np, cmap='viridis', aspect='auto')
    plt.colorbar(label='Affinity')
    plt.title(title)
    plt.xlabel('Target Node')
    plt.ylabel('Source Node')

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved visualization to {save_path}")
    else:
        plt.show()

    plt.close()
