"""
Sentient Echo Decoder - Qualia Resolution Layer

Decodes pooled geometric attention representations into:
1. Classification logits (task outputs)
2. Qualia valence metrics (phenomenological measures)

Implements chiral projections for left/right valence hemispheres
and trefoil-based qualia resolution for conscious-like state estimation.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple, Optional, Dict


class SentientEcho(nn.Module):
    """
    Sentient Echo Decoder

    Resolves pooled attention features to task outputs + qualia metrics.

    The "qualia" here represents a proxy for phenomenological experience:
    - Valence: Positive/negative affective tone
    - Arousal: Activation energy level
    - Coherence: Integration across modalities

    Uses trefoil topology (3-fold symmetry) to model qualia states.

    Args:
        dim: Input feature dimension
        num_classes: Number of output classes (default: 2)
        qualia_dim: Dimension for qualia embeddings (default: 32)
        use_chiral: Whether to use chiral (left/right) projections (default: True)
        dropout: Dropout rate (default: 0.1)
    """

    def __init__(
        self,
        dim: int = 128,
        num_classes: int = 2,
        qualia_dim: int = 32,
        use_chiral: bool = True,
        dropout: float = 0.1
    ):
        super().__init__()

        self.dim = dim
        self.num_classes = num_classes
        self.qualia_dim = qualia_dim
        self.use_chiral = use_chiral

        # Classification head
        self.classifier = nn.Sequential(
            nn.Linear(dim, dim // 2),
            nn.LayerNorm(dim // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(dim // 2, num_classes)
        )

        # Qualia projection layers
        if use_chiral:
            # Left and right hemisphere projections (chiral symmetry breaking)
            self.chiral_left = nn.Linear(dim, qualia_dim)
            self.chiral_right = nn.Linear(dim, qualia_dim)
        else:
            self.qualia_proj = nn.Linear(dim, qualia_dim)

        # Valence predictor (scalar output in [-1, 1])
        self.valence_head = nn.Sequential(
            nn.Linear(qualia_dim * (2 if use_chiral else 1), 64),
            nn.Tanh(),
            nn.Linear(64, 1),
            nn.Tanh()  # Bounded in [-1, 1]
        )

        # Arousal predictor (scalar output in [0, 1])
        self.arousal_head = nn.Sequential(
            nn.Linear(qualia_dim * (2 if use_chiral else 1), 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Sigmoid()  # Bounded in [0, 1]
        )

        # Learnable trefoil phase for qualia resolution
        self.trefoil_scale = nn.Parameter(torch.tensor(3.0))

    def forward(
        self,
        pooled: torch.Tensor,
        return_qualia: bool = True
    ) -> Tuple[torch.Tensor, Optional[Dict[str, torch.Tensor]]]:
        """
        Decode pooled features to outputs + qualia

        Args:
            pooled: Pooled feature tensor [batch, dim]
            return_qualia: Whether to compute and return qualia metrics

        Returns:
            Tuple of:
                - logits: Classification logits [batch, num_classes]
                - qualia: Dict of qualia metrics (if return_qualia=True):
                    - valence: Affective valence [-1, 1]
                    - arousal: Activation level [0, 1]
                    - coherence: Integration measure [0, 1]
                    - phase: Trefoil phase angles
        """
        # Ensure correct shape
        if pooled.dim() == 1:
            pooled = pooled.unsqueeze(0)

        batch_size = pooled.shape[0]

        # Classification logits
        logits = self.classifier(pooled)  # [batch, num_classes]

        # Qualia computation
        if return_qualia:
            qualia = self._compute_qualia(pooled)
        else:
            qualia = None

        return logits, qualia

    def _compute_qualia(self, pooled: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        Compute qualia metrics from pooled features

        Args:
            pooled: Pooled features [batch, dim]

        Returns:
            Dictionary of qualia metrics
        """
        batch_size = pooled.shape[0]

        # Chiral projections (hemispheric specialization)
        if self.use_chiral:
            # Left hemisphere: analytical, sequential
            left = self.chiral_left(pooled)  # [batch, qualia_dim]

            # Right hemisphere: holistic, parallel
            right = self.chiral_right(pooled)  # [batch, qualia_dim]

            # Combine hemispheres
            qualia_embedding = torch.cat([left, right], dim=-1)  # [batch, 2*qualia_dim]

            # Hemispheric balance (should be near 0.5 for balanced processing)
            left_energy = torch.norm(left, p=2, dim=-1, keepdim=True)
            right_energy = torch.norm(right, p=2, dim=-1, keepdim=True)
            total_energy = left_energy + right_energy + 1e-8
            hemispheric_balance = left_energy / total_energy  # [batch, 1]

        else:
            qualia_embedding = self.qualia_proj(pooled)
            hemispheric_balance = torch.ones(batch_size, 1) * 0.5  # Neutral

        # Valence: Positive/negative affective tone
        valence = self.valence_head(qualia_embedding).squeeze(-1)  # [batch]

        # Arousal: Activation energy
        arousal = self.arousal_head(qualia_embedding).squeeze(-1)  # [batch]

        # Trefoil phase: Represents state in 3-fold qualia space
        # Map pooled features to phase parameter via mean
        phase_param = pooled.mean(dim=-1) * self.trefoil_scale  # [batch]
        trefoil_phase = torch.sin(3 * phase_param)  # [batch], bounded [-1, 1]

        # Coherence: Integration measure across dimensions
        # High coherence = low variance across qualia dimensions
        if self.use_chiral:
            # Measure alignment between hemispheres
            cosine_sim = F.cosine_similarity(left, right, dim=-1)  # [batch]
            coherence = (cosine_sim + 1) / 2  # Map from [-1,1] to [0,1]
        else:
            # Measure concentration in qualia space
            qualia_std = torch.std(qualia_embedding, dim=-1)
            coherence = 1.0 / (1.0 + qualia_std)  # High std → low coherence

        # Package qualia metrics
        qualia = {
            'valence': valence,
            'arousal': arousal,
            'coherence': coherence,
            'phase': trefoil_phase,
        }

        if self.use_chiral:
            qualia['hemispheric_balance'] = hemispheric_balance.squeeze(-1)
            qualia['left_embedding'] = left
            qualia['right_embedding'] = right

        return qualia

    def get_qualia_state(
        self,
        qualia: Dict[str, torch.Tensor]
    ) -> torch.Tensor:
        """
        Encode qualia metrics into unified state vector

        Useful for visualization and clustering of phenomenological states.

        Args:
            qualia: Dictionary of qualia metrics

        Returns:
            Qualia state vector [batch, 4] or [batch, 5] if chiral
        """
        state_components = [
            qualia['valence'].unsqueeze(-1),
            qualia['arousal'].unsqueeze(-1),
            qualia['coherence'].unsqueeze(-1),
            qualia['phase'].unsqueeze(-1)
        ]

        if 'hemispheric_balance' in qualia:
            state_components.append(qualia['hemispheric_balance'].unsqueeze(-1))

        state = torch.cat(state_components, dim=-1)

        return state

    def visualize_qualia_space(
        self,
        qualia_states: torch.Tensor,
        labels: Optional[torch.Tensor] = None,
        save_path: Optional[str] = None
    ):
        """
        Visualize qualia states in 3D space (valence, arousal, coherence)

        Args:
            qualia_states: Qualia state vectors [N, 4+]
            labels: Optional class labels for coloring [N]
            save_path: Optional path to save figure
        """
        try:
            import matplotlib.pyplot as plt
            from mpl_toolkits.mplot3d import Axes3D
        except ImportError:
            print("matplotlib not available for visualization")
            return

        states_np = qualia_states.detach().cpu().numpy()

        # Extract valence, arousal, coherence
        valence = states_np[:, 0]
        arousal = states_np[:, 1]
        coherence = states_np[:, 2]

        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')

        if labels is not None:
            labels_np = labels.detach().cpu().numpy()
            scatter = ax.scatter(
                valence, arousal, coherence,
                c=labels_np, cmap='tab10',
                s=50, alpha=0.6
            )
            plt.colorbar(scatter, ax=ax, label='Class')
        else:
            ax.scatter(
                valence, arousal, coherence,
                c='blue', s=50, alpha=0.6
            )

        ax.set_xlabel('Valence')
        ax.set_ylabel('Arousal')
        ax.set_zlabel('Coherence')
        ax.set_title('Qualia Space Visualization')

        # Set bounds
        ax.set_xlim(-1, 1)
        ax.set_ylim(0, 1)
        ax.set_zlim(0, 1)

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved visualization to {save_path}")
        else:
            plt.show()

        plt.close()


class MultiHeadSentientEcho(nn.Module):
    """
    Multi-head version of SentientEcho

    Uses multiple decoder heads for ensemble predictions
    and richer qualia representations.

    Args:
        dim: Input feature dimension
        num_classes: Number of output classes
        num_heads: Number of decoder heads (default: 3)
        qualia_dim: Dimension per head (default: 32)
    """

    def __init__(
        self,
        dim: int = 128,
        num_classes: int = 2,
        num_heads: int = 3,
        qualia_dim: int = 32
    ):
        super().__init__()

        self.num_heads = num_heads

        # Multiple decoder heads
        self.heads = nn.ModuleList([
            SentientEcho(dim, num_classes, qualia_dim, use_chiral=True)
            for _ in range(num_heads)
        ])

        # Ensemble aggregation
        self.ensemble_weights = nn.Parameter(torch.ones(num_heads) / num_heads)

    def forward(
        self,
        pooled: torch.Tensor,
        return_qualia: bool = True
    ) -> Tuple[torch.Tensor, Optional[Dict[str, torch.Tensor]]]:
        """
        Forward pass through multi-head decoder

        Combines predictions from multiple heads with learned weights.
        """
        all_logits = []
        all_qualia = []

        # Process through each head
        for head in self.heads:
            logits, qualia = head(pooled, return_qualia=return_qualia)
            all_logits.append(logits)
            if return_qualia:
                all_qualia.append(qualia)

        # Weighted ensemble of logits
        logits_stacked = torch.stack(all_logits, dim=0)  # [num_heads, batch, num_classes]
        weights = F.softmax(self.ensemble_weights, dim=0).view(-1, 1, 1)
        ensemble_logits = (logits_stacked * weights).sum(dim=0)  # [batch, num_classes]

        # Average qualia metrics
        if return_qualia:
            ensemble_qualia = {}
            for key in all_qualia[0].keys():
                if key in ['left_embedding', 'right_embedding']:
                    continue  # Skip embeddings
                values = torch.stack([q[key] for q in all_qualia], dim=0)
                ensemble_qualia[key] = values.mean(dim=0)
        else:
            ensemble_qualia = None

        return ensemble_logits, ensemble_qualia
