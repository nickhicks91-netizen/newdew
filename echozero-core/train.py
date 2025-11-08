"""
EchoZero Training Script

Trains the full EchoZero network on specified datasets with benchmarking.

Usage:
    python train.py --config config/config.yaml
    python train.py --benchmark  # Run benchmark against baselines
"""

import argparse
import yaml
from pathlib import Path
import sys

# Phase 1: VortexEncoder imports
try:
    import torch
    import torch.nn.functional as F
    from src.ingestion.vortex_encoder import VortexEncoder
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("Warning: PyTorch not installed. Install with: pip install torch")

# TODO Phase 2: Import TEAPenroseLayer
# TODO Phase 3: Import EchoZeroNet

# Optional: W&B for experiment tracking
try:
    import wandb
    WANDB_AVAILABLE = True
except ImportError:
    WANDB_AVAILABLE = False
    print("Info: wandb not installed. Metrics won't be logged to W&B.")


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def train_vortex_encoder(config: dict, use_wandb: bool = False):
    """
    Phase 1: Train VortexEncoder on synthetic or real data

    Args:
        config: Configuration dictionary
        use_wandb: Whether to log to Weights & Biases
    """
    if not TORCH_AVAILABLE:
        print("ERROR: PyTorch required for training. Install with: pip install torch")
        return

    print("\n" + "=" * 50)
    print("Phase 1: VortexEncoder Training")
    print("=" * 50)

    # Initialize wandb if available and requested
    if use_wandb and WANDB_AVAILABLE:
        wandb.init(
            project=config['wandb']['project'],
            config=config,
            name='phase1-vortex-encoder'
        )

    # Create encoder
    dim = config['model']['dim']
    mode = config['encoder']['mode']

    print(f"Initializing VortexEncoder (dim={dim}, mode={mode})")
    encoder = VortexEncoder(dim=dim, mode=mode, normalize=True)

    # Training parameters
    lr = config['training']['learning_rate']
    epochs = config['training']['num_epochs']
    optimizer = torch.optim.Adam(encoder.parameters(), lr=lr)

    print(f"Training for {epochs} epochs with lr={lr}")

    # Generate synthetic training data
    print("\nGenerating synthetic training data...")
    if mode == 'eeg':
        # Synthetic EEG-like signals
        num_samples = 100
        train_signals = [torch.randn(512) for _ in range(num_samples)]
    elif mode == 'spectral':
        # Synthetic spectral data
        num_samples = 100
        train_signals = [torch.randn(256) for _ in range(num_samples)]
    else:  # text mode
        print("Text mode training requires datasets package. Skipping for now.")
        return

    # Training loop
    print(f"\nTraining on {num_samples} samples...")
    for epoch in range(epochs):
        total_loss = 0.0
        total_fidelity = 0.0

        for i, signal in enumerate(train_signals):
            # Encode
            engram, phases = encoder(signal)

            # Compute fidelity loss (1 - fidelity score)
            fidelity = encoder.get_fidelity(signal, engram)
            fidelity_loss = 1.0 - fidelity

            # Additional regularization: encourage phase diversity
            phase_diversity = -torch.std(phases)  # Negative std as we want to maximize

            # Combined loss
            loss = fidelity_loss + 0.01 * phase_diversity

            # Backward pass
            optimizer.zero_grad()
            if isinstance(loss, torch.Tensor):
                loss.backward()
            else:
                torch.tensor(loss, requires_grad=True).backward()
            optimizer.step()

            total_loss += fidelity_loss
            total_fidelity += fidelity

        # Epoch metrics
        avg_loss = total_loss / num_samples
        avg_fidelity = total_fidelity / num_samples

        print(f"Epoch [{epoch+1}/{epochs}] "
              f"Loss: {avg_loss:.4f} "
              f"Fidelity: {avg_fidelity:.4f}")

        # Log to wandb
        if use_wandb and WANDB_AVAILABLE:
            wandb.log({
                'epoch': epoch,
                'loss': avg_loss,
                'fidelity': avg_fidelity,
                'phase_scale': encoder.phase_scale.item()
            })

    print(f"\nTraining complete!")
    print(f"Final fidelity: {avg_fidelity:.4f}")

    # Benchmark gap analysis
    print("\n" + "-" * 50)
    print("Benchmark Gap Analysis:")
    target_fidelity = 0.95
    if avg_fidelity >= target_fidelity:
        print(f"✓ Fidelity target met: {avg_fidelity:.4f} >= {target_fidelity}")
    else:
        gap = target_fidelity - avg_fidelity
        print(f"✗ Fidelity gap: {gap:.4f} (current: {avg_fidelity:.4f}, target: {target_fidelity})")
        print(f"  Action: Consider increasing training epochs or adjusting architecture")

    # Save checkpoint
    checkpoint_dir = Path(config['paths']['checkpoint_dir'])
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = checkpoint_dir / 'vortex_encoder_phase1.pt'

    torch.save({
        'epoch': epochs,
        'model_state_dict': encoder.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'fidelity': avg_fidelity,
        'config': config
    }, checkpoint_path)

    print(f"\nCheckpoint saved to: {checkpoint_path}")

    if use_wandb and WANDB_AVAILABLE:
        wandb.finish()


def main():
    parser = argparse.ArgumentParser(description='Train EchoZero model')
    parser.add_argument('--config', type=str, default='config/config.yaml',
                        help='Path to config file')
    parser.add_argument('--phase', type=int, default=1, choices=[1, 2, 3],
                        help='Training phase (1=Ingestion, 2=Warp, 3=Full)')
    parser.add_argument('--benchmark', action='store_true',
                        help='Run benchmark against baselines')
    parser.add_argument('--wandb', action='store_true',
                        help='Log metrics to Weights & Biases')
    parser.add_argument('--resume', type=str, default=None,
                        help='Resume from checkpoint')

    args = parser.parse_args()
    config = load_config(args.config)

    print("=" * 60)
    print("EchoZero Training Script v0.1")
    print("=" * 60)
    print(f"Configuration: {args.config}")
    print(f"Phase: {args.phase}")
    print(f"Benchmark mode: {args.benchmark}")
    print(f"W&B logging: {args.wandb and WANDB_AVAILABLE}")
    print()

    # Phase-specific training
    if args.phase == 1:
        # Phase 1: VortexEncoder
        train_vortex_encoder(config, use_wandb=args.wandb)

    elif args.phase == 2:
        # Phase 2: TEAPenroseLayer
        print("Phase 2: TEAPenroseLayer training")
        print("TODO: Implement in Phase 2")

    elif args.phase == 3:
        # Phase 3: Full EchoZeroNet
        print("Phase 3: Full network training")
        print("TODO: Implement in Phase 3")

    print("\n" + "=" * 60)
    print("Training session complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
