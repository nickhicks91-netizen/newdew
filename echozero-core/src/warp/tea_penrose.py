"""
TEAPenroseLayer - Torsion-Enhanced Attention on Penrose Tilings

Complete geometric attention layer combining:
1. Penrose P3 aperiodic node positions
2. Ricci-warped distance metrics
3. Torsion-based phase routing

Implements coherence funneling through topologically-structured attention.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple, Optional

from .penrose_gen import generate_penrose
from .ricci_affinity import ricci_affinity, ricci_warp
from .torsion_router import torsion_loss, trefoil_phase, coherence_score


class TEAPenroseLayer(nn.Module):
    """
    Torsion-Enhanced Attention on Penrose Lattice

    Geometric attention layer with:
    - Aperiodic Penrose P3 node positions (fixed or learnable)
    - Ricci-curvature distance warping
    - Torsion-based phase routing
    - Multi-head attention with geometric modulation

    Args:
        num_nodes: Number of attention nodes in Penrose tiling
        dim: Feature dimension
        ricci: Ricci curvature parameter (default: -2.0 for hyperbolic)
        penrose_level: Penrose subdivision depth (default: 2)
        num_heads: Number of attention heads (default: 4)
        torsion_scale: Torsion penalty scaling (default: 0.1)
        learnable_positions: Whether node positions are learnable (default: False)
        temperature: Softmax temperature (default: 1.0)
    """

    def __init__(
        self,
        num_nodes: int = 20,
        dim: int = 128,
        ricci: float = -2.0,
        penrose_level: int = 2,
        num_heads: int = 4,
        torsion_scale: float = 0.1,
        learnable_positions: bool = False,
        temperature: float = 1.0
    ):
        super().__init__()

        self.num_nodes = num_nodes
        self.dim = dim
        self.ricci = ricci
        self.penrose_level = penrose_level
        self.num_heads = num_heads
        self.torsion_scale = torsion_scale
        self.temperature = temperature

        # Generate initial Penrose positions
        initial_positions = generate_penrose(
            level=penrose_level,
            num_nodes=num_nodes,
            scale=1.0,
            seed=42  # Reproducible
        )

        # Store positions (learnable or fixed)
        if learnable_positions:
            self.positions = nn.Parameter(initial_positions)
        else:
            self.register_buffer('positions', initial_positions)

        # Generate trefoil phases for each node
        # Use position-based parameter for phase consistency
        t_vals = torch.linspace(0, 2 * torch.pi, num_nodes)
        initial_phases = trefoil_phase(t_vals)  # [num_nodes]

        # Expand to full dimension and make learnable
        self.torsion_phases = nn.Parameter(
            initial_phases.unsqueeze(1).repeat(1, dim)  # [num_nodes, dim]
        )

        # Learnable torsion scale
        self.torsion_scale_param = nn.Parameter(torch.tensor(torsion_scale))

        # Multi-head projections
        assert dim % num_heads == 0, "dim must be divisible by num_heads"
        self.head_dim = dim // num_heads

        # Separate Q, K, V projections for each head
        self.query_proj = nn.Linear(dim, dim)
        self.key_proj = nn.Linear(dim, dim)
        self.value_proj = nn.Linear(dim, dim)

        # Output projection
        self.out_proj = nn.Linear(dim, dim)

        # Layer normalization
        self.norm = nn.LayerNorm(dim)

    def forward(
        self,
        x: torch.Tensor,
        return_attention: bool = True,
        return_metrics: bool = False
    ) -> Tuple[torch.Tensor, ...]:
        """
        Forward pass through TEAPenroseLayer

        Args:
            x: Input tensor [batch, dim] or [batch, seq_len, dim]
            return_attention: Whether to return attention weights
            return_metrics: Whether to return coherence/torsion metrics

        Returns:
            Tuple of:
                - output: Attended features [batch, dim] or [batch, seq_len, dim]
                - attention: Attention weights [batch, num_nodes, num_nodes] (optional)
                - metrics: Dict of coherence/torsion metrics (optional)
        """
        # Handle different input shapes
        if x.dim() == 2:
            # [batch, dim] → [batch, 1, dim]
            x = x.unsqueeze(1)
            squeeze_output = True
        else:
            squeeze_output = False

        batch_size, seq_len, _ = x.shape

        # Project to nodes via learnable attention
        # Step 1: Compute Q, K, V
        Q = self.query_proj(x)  # [batch, seq_len, dim]
        K = self.key_proj(x)    # [batch, seq_len, dim]
        V = self.value_proj(x)  # [batch, seq_len, dim]

        # Step 2: Expand features to nodes
        # Simple approach: repeat features for each node
        node_features = x.mean(dim=1).unsqueeze(1).repeat(1, self.num_nodes, 1)  # [batch, num_nodes, dim]

        # Step 3: Compute geometric attention
        attention, torsion_penalty = self._compute_geometric_attention(
            node_features,
            batch_size
        )

        # Step 4: Apply attention to aggregate node features
        attended = torch.bmm(attention, node_features)  # [batch, num_nodes, dim]

        # Step 5: Pool across nodes
        output = attended.mean(dim=1, keepdim=True)  # [batch, 1, dim]

        # Residual connection + normalization
        output = self.norm(output + x.mean(dim=1, keepdim=True))

        # Expand back to seq_len if needed
        if not squeeze_output and seq_len > 1:
            output = output.repeat(1, seq_len, 1)
        elif squeeze_output:
            output = output.squeeze(1)

        # Prepare return values
        returns = [output]

        if return_attention:
            returns.append(attention)

        if return_metrics:
            metrics = {
                'coherence': coherence_score(self.torsion_phases.unsqueeze(0)),
                'torsion_mean': torsion_penalty.mean(),
                'torsion_std': torsion_penalty.std(),
                'attention_entropy': self._compute_entropy(attention),
                'attention_std': attention.std(dim=-1).mean()
            }
            returns.append(metrics)

        return tuple(returns) if len(returns) > 1 else returns[0]

    def _compute_geometric_attention(
        self,
        node_features: torch.Tensor,
        batch_size: int
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Compute attention weights with Ricci warping and torsion routing

        Args:
            node_features: Node feature tensor [batch, num_nodes, dim]
            batch_size: Batch size

        Returns:
            Tuple of:
                - attention: Attention weights [batch, num_nodes, num_nodes]
                - torsion_penalty: Torsion penalties [batch, num_nodes, num_nodes]
        """
        # Expand positions for batch
        pos_batch = self.positions.unsqueeze(0).expand(batch_size, -1, -1)  # [batch, num_nodes, 3]

        # Compute Ricci-warped affinities
        geometric_affinity = ricci_affinity(
            pos_batch,
            ricci=self.ricci,
            temperature=self.temperature,
            normalize=False  # We'll combine with torsion first
        )  # [batch, num_nodes, num_nodes]

        # Compute torsion penalties from phase mismatch
        phases_batch = self.torsion_phases.unsqueeze(0).expand(batch_size, -1, -1)  # [batch, num_nodes, dim]

        torsion_penalty = torsion_loss(
            phases_batch,
            phases_batch,
            scale=self.torsion_scale_param.abs(),  # Ensure positive
            mode='l2'
        )  # [batch, num_nodes, num_nodes]

        # Combine geometric affinity with torsion modulation
        # exp(-torsion) reduces attention for phase-mismatched pairs
        torsion_modulation = torch.exp(-torsion_penalty)

        # Combined attention logits
        attention_logits = geometric_affinity * torsion_modulation

        # Softmax normalization
        attention = F.softmax(attention_logits, dim=-1)

        return attention, torsion_penalty

    def _compute_entropy(self, attention: torch.Tensor) -> torch.Tensor:
        """
        Compute entropy of attention distribution

        Lower entropy = more focused attention (coherence funneling)

        Args:
            attention: Attention weights [batch, num_nodes, num_nodes]

        Returns:
            Mean entropy across batch
        """
        # Clip for numerical stability
        attention_clipped = torch.clamp(attention, min=1e-9)

        # Entropy: -sum(p * log(p))
        entropy = -(attention_clipped * torch.log(attention_clipped)).sum(dim=-1)  # [batch, num_nodes]

        return entropy.mean()

    def get_effective_graph(
        self,
        threshold: float = 0.1
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Extract effective graph structure from attention

        Identifies strong connections (attention > threshold).

        Args:
            threshold: Minimum attention weight for edge

        Returns:
            Tuple of:
                - edge_index: Edge indices [2, num_edges]
                - edge_weight: Edge weights [num_edges]
        """
        # Compute attention for dummy input
        dummy_input = torch.zeros(1, self.dim)
        _, attention = self.forward(dummy_input, return_attention=True)
        attention = attention.squeeze(0)  # [num_nodes, num_nodes]

        # Find edges above threshold
        edge_mask = attention > threshold
        edge_index = edge_mask.nonzero(as_tuple=False).T  # [2, num_edges]
        edge_weight = attention[edge_mask]  # [num_edges]

        return edge_index, edge_weight

    def visualize_layer(
        self,
        save_path: Optional[str] = None,
        show_attention: bool = True
    ):
        """
        Visualize layer structure

        Args:
            save_path: Optional path to save figure
            show_attention: Whether to overlay attention strengths
        """
        try:
            import matplotlib.pyplot as plt
            import numpy as np
        except ImportError:
            print("matplotlib not available for visualization")
            return

        pos_np = self.positions.detach().cpu().numpy()
        phases_np = self.torsion_phases.detach().cpu().numpy()

        fig, axes = plt.subplots(1, 2 if show_attention else 1, figsize=(16 if show_attention else 8, 8))

        if not show_attention:
            axes = [axes]

        # Left: Node positions colored by average phase
        avg_phase = phases_np.mean(axis=1)
        scatter = axes[0].scatter(
            pos_np[:, 0],
            pos_np[:, 1],
            c=avg_phase,
            cmap='twilight',
            s=200,
            alpha=0.7,
            edgecolors='black',
            linewidths=2
        )
        axes[0].set_title(f'Penrose P3 Nodes (Level {self.penrose_level})')
        axes[0].set_xlabel('X')
        axes[0].set_ylabel('Y')
        axes[0].axis('equal')
        plt.colorbar(scatter, ax=axes[0], label='Average Phase')

        # Right: Attention matrix (if requested)
        if show_attention:
            dummy_input = torch.zeros(1, self.dim)
            _, attention = self.forward(dummy_input, return_attention=True)
            attention_np = attention.squeeze(0).detach().cpu().numpy()

            im = axes[1].imshow(attention_np, cmap='viridis', aspect='auto')
            axes[1].set_title('Geometric Attention Matrix')
            axes[1].set_xlabel('Target Node')
            axes[1].set_ylabel('Source Node')
            plt.colorbar(im, ax=axes[1], label='Attention Weight')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved visualization to {save_path}")
        else:
            plt.show()

        plt.close()
