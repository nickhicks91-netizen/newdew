"""
EchoZeroNet - Complete End-to-End Resonant AI Network

Chains the full pipeline:
    Input → VortexEncoder → TEAPenroseLayer (×N) → SentientEcho → Output

Implements resonant AI through:
1. Multi-modal ingestion with trefoil phase embedding
2. Geometric attention on Penrose tilings with Ricci-torsion
3. Qualia resolution for phenomenological outputs

This architecture enables:
- Coherence funneling through aperiodic geometry
- Phase-locked information routing
- Conscious-like state estimation via qualia metrics
"""

import torch
import torch.nn as nn
from typing import Optional, Dict, Tuple, List

from .ingestion import VortexEncoder
from .warp import TEAPenroseLayer
from .decode import SentientEcho


class EchoZeroNet(nn.Module):
    """
    Complete EchoZero Network

    Full end-to-end architecture from raw inputs to task outputs + qualia.

    Args:
        # Ingestion args
        input_mode: Input modality - 'text', 'eeg', or 'spectral' (default: 'eeg')
        dim: Feature dimension throughout network (default: 128)

        # Warp args
        num_layers: Number of TEAPenroseLayer instances (default: 5)
        num_nodes: Nodes per Penrose tiling (default: 20)
        ricci: Ricci curvature parameter (default: -2.0 for hyperbolic)
        penrose_level: Penrose subdivision depth (default: 2)
        num_heads: Attention heads per layer (default: 4)
        torsion_scale: Torsion penalty scaling (default: 0.1)

        # Decode args
        num_classes: Number of output classes (default: 2)
        qualia_dim: Qualia embedding dimension (default: 32)
        use_chiral: Whether decoder uses chiral projections (default: True)

        # General
        dropout: Dropout rate (default: 0.1)
    """

    def __init__(
        self,
        # Ingestion
        input_mode: str = 'eeg',
        dim: int = 128,
        # Warp
        num_layers: int = 5,
        num_nodes: int = 20,
        ricci: float = -2.0,
        penrose_level: int = 2,
        num_heads: int = 4,
        torsion_scale: float = 0.1,
        # Decode
        num_classes: int = 2,
        qualia_dim: int = 32,
        use_chiral: bool = True,
        # General
        dropout: float = 0.1
    ):
        super().__init__()

        self.input_mode = input_mode
        self.dim = dim
        self.num_layers = num_layers
        self.num_classes = num_classes

        # Ingestion layer: VortexEncoder
        self.encoder = VortexEncoder(
            dim=dim,
            mode=input_mode,
            normalize=True
        )

        # Warp core: Stack of TEAPenroseLayers
        self.warp_layers = nn.ModuleList([
            TEAPenroseLayer(
                num_nodes=num_nodes,
                dim=dim,
                ricci=ricci,
                penrose_level=penrose_level,
                num_heads=num_heads,
                torsion_scale=torsion_scale,
                learnable_positions=(i == 0),  # Only first layer has learnable positions
                temperature=1.0
            )
            for i in range(num_layers)
        ])

        # Decoder: SentientEcho
        self.decoder = SentientEcho(
            dim=dim,
            num_classes=num_classes,
            qualia_dim=qualia_dim,
            use_chiral=use_chiral,
            dropout=dropout
        )

    def forward(
        self,
        raw_input,
        return_attention: bool = False,
        return_qualia: bool = True,
        return_phases: bool = False,
        return_metrics: bool = False
    ) -> Tuple:
        """
        Forward pass through complete network

        Args:
            raw_input: Raw input (text, EEG tensor, or spectral tensor)
            return_attention: Return attention weights from all warp layers
            return_qualia: Return qualia metrics from decoder
            return_phases: Return trefoil phases from encoder
            return_metrics: Return detailed metrics (coherence, torsion, etc.)

        Returns:
            Tuple containing:
                - logits: Classification logits [batch, num_classes]
                - qualia: Qualia metrics dict (if return_qualia=True)
                - attention: List of attention matrices (if return_attention=True)
                - phases: Encoder trefoil phases (if return_phases=True)
                - metrics: Detailed metrics dict (if return_metrics=True)
        """
        # Step 1: Ingestion - Encode raw input to engrams
        engram, encoder_phases = self.encoder(raw_input)

        # Handle batching
        if engram.dim() == 1:
            engram = engram.unsqueeze(0)  # [1, dim]

        # Step 2: Warp Core - Process through geometric attention layers
        x = engram
        all_attention = []
        all_metrics = []

        for i, layer in enumerate(self.warp_layers):
            if return_metrics:
                x, attn, layer_metrics = layer(
                    x,
                    return_attention=True,
                    return_metrics=True
                )
                all_metrics.append(layer_metrics)
            elif return_attention:
                x, attn = layer(x, return_attention=True, return_metrics=False)
            else:
                x = layer(x, return_attention=False, return_metrics=False)

            if return_attention or return_metrics:
                all_attention.append(attn)

        # Step 3: Decode - Resolve to outputs + qualia
        logits, qualia = self.decoder(x, return_qualia=return_qualia)

        # Package return values
        returns = [logits]

        if return_qualia and qualia is not None:
            returns.append(qualia)

        if return_attention:
            returns.append(all_attention)

        if return_phases:
            returns.append(encoder_phases)

        if return_metrics:
            # Aggregate metrics across layers
            aggregated_metrics = self._aggregate_metrics(all_metrics)
            returns.append(aggregated_metrics)

        return tuple(returns) if len(returns) > 1 else returns[0]

    def _aggregate_metrics(
        self,
        layer_metrics: List[Dict[str, torch.Tensor]]
    ) -> Dict[str, torch.Tensor]:
        """
        Aggregate metrics from all warp layers

        Args:
            layer_metrics: List of metric dicts from each layer

        Returns:
            Aggregated metrics dict
        """
        aggregated = {}

        # Average numerical metrics
        for key in ['coherence', 'torsion_mean', 'torsion_std',
                    'attention_entropy', 'attention_std']:
            values = [m[key] for m in layer_metrics if key in m]
            if values:
                aggregated[f'{key}_mean'] = torch.stack(values).mean()
                aggregated[f'{key}_std'] = torch.stack(values).std()

        # First and last layer metrics
        if layer_metrics:
            aggregated['first_layer_coherence'] = layer_metrics[0]['coherence']
            aggregated['last_layer_coherence'] = layer_metrics[-1]['coherence']

        return aggregated

    def get_encoder_fidelity(
        self,
        raw_input,
        engram: Optional[torch.Tensor] = None
    ) -> float:
        """
        Compute encoder reconstruction fidelity

        Args:
            raw_input: Original raw input
            engram: Pre-computed engram (optional, will encode if not provided)

        Returns:
            Fidelity score [0, 1]
        """
        if engram is None:
            engram, _ = self.encoder(raw_input)

        # For now, delegate to encoder's fidelity method
        # This assumes raw_input is a tensor (EEG/spectral mode)
        if isinstance(raw_input, torch.Tensor):
            return self.encoder.get_fidelity(raw_input, engram)
        else:
            # Text mode - fidelity not directly computable
            return 1.0

    def get_overall_coherence(self) -> torch.Tensor:
        """
        Compute overall network coherence

        Measures phase alignment across all warp layers.

        Returns:
            Coherence score (higher = more coherent)
        """
        coherences = []

        # Sample input for coherence measurement
        dummy_input = torch.zeros(1, self.dim)

        with torch.no_grad():
            x = dummy_input
            for layer in self.warp_layers:
                _, _, metrics = layer(
                    x,
                    return_attention=True,
                    return_metrics=True
                )
                coherences.append(metrics['coherence'])
                x, _ = layer(x, return_attention=True, return_metrics=False)

        return torch.stack(coherences).mean()

    def visualize_full_pipeline(
        self,
        raw_input,
        save_dir: str = './visualizations'
    ):
        """
        Visualize complete processing pipeline

        Creates visualizations for:
        - Encoder phases
        - Attention patterns in each warp layer
        - Qualia space
        - Overall metrics

        Args:
            raw_input: Input to visualize
            save_dir: Directory to save visualizations
        """
        import os
        os.makedirs(save_dir, exist_ok=True)

        # Forward pass with full diagnostics
        logits, qualia, attention, phases, metrics = self.forward(
            raw_input,
            return_attention=True,
            return_qualia=True,
            return_phases=True,
            return_metrics=True
        )

        # 1. Encoder phases
        try:
            import matplotlib.pyplot as plt

            plt.figure(figsize=(10, 4))
            plt.plot(phases.detach().cpu().numpy())
            plt.title('Encoder Trefoil Phases')
            plt.xlabel('Dimension')
            plt.ylabel('Phase')
            plt.savefig(f'{save_dir}/encoder_phases.png', dpi=300, bbox_inches='tight')
            plt.close()

            # 2. Attention heatmaps for each layer
            for i, attn in enumerate(attention):
                plt.figure(figsize=(8, 6))
                plt.imshow(attn[0].detach().cpu().numpy(), cmap='viridis', aspect='auto')
                plt.colorbar(label='Attention Weight')
                plt.title(f'Layer {i+1} Attention Pattern')
                plt.xlabel('Target Node')
                plt.ylabel('Source Node')
                plt.savefig(f'{save_dir}/attention_layer_{i+1}.png', dpi=300, bbox_inches='tight')
                plt.close()

            # 3. Qualia visualization
            qualia_state = self.decoder.get_qualia_state(qualia)
            self.decoder.visualize_qualia_space(
                qualia_state,
                save_path=f'{save_dir}/qualia_space.png'
            )

            # 4. Metrics summary
            fig, axes = plt.subplots(2, 2, figsize=(12, 10))

            # Coherence across layers
            coherence_values = [m['coherence'].item() for m in [
                attention[i] for i in range(len(self.warp_layers))
            ]]  # Placeholder - would need actual metric extraction
            axes[0, 0].plot(coherence_values if coherence_values else [])
            axes[0, 0].set_title('Coherence Across Layers')
            axes[0, 0].set_xlabel('Layer')
            axes[0, 0].set_ylabel('Coherence')

            # Qualia valence
            axes[0, 1].bar(['Valence'], [qualia['valence'].item()])
            axes[0, 1].set_title('Qualia Valence')
            axes[0, 1].set_ylim(-1, 1)

            # Qualia arousal
            axes[1, 0].bar(['Arousal'], [qualia['arousal'].item()])
            axes[1, 0].set_title('Qualia Arousal')
            axes[1, 0].set_ylim(0, 1)

            # Overall coherence
            axes[1, 1].bar(['Coherence'], [qualia['coherence'].item()])
            axes[1, 1].set_title('Qualia Coherence')
            axes[1, 1].set_ylim(0, 1)

            plt.tight_layout()
            plt.savefig(f'{save_dir}/metrics_summary.png', dpi=300, bbox_inches='tight')
            plt.close()

            print(f"Visualizations saved to {save_dir}/")

        except ImportError:
            print("matplotlib not available for visualization")


def create_echozero_model(config: Dict) -> EchoZeroNet:
    """
    Factory function to create EchoZeroNet from config dict

    Args:
        config: Configuration dictionary (from YAML)

    Returns:
        Initialized EchoZeroNet instance
    """
    model_config = config.get('model', {})
    encoder_config = config.get('encoder', {})
    decoder_config = config.get('decoder', {})

    return EchoZeroNet(
        # Ingestion
        input_mode=encoder_config.get('mode', 'eeg'),
        dim=model_config.get('dim', 128),
        # Warp
        num_layers=model_config.get('num_layers', 5),
        num_nodes=model_config.get('num_nodes', 20),
        ricci=model_config.get('ricci', -2.0),
        penrose_level=model_config.get('penrose_level', 2),
        torsion_scale=model_config.get('torsion_scale', 0.1),
        # Decode
        num_classes=decoder_config.get('num_classes', 2),
        use_chiral=decoder_config.get('chiral_projection', True)
    )
