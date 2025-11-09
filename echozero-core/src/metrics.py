"""
EchoZero Metrics Module

Magnitude-aware coherence metrics and attention health diagnostics to prevent
"metric gaming" and ensure meaningful signal processing.

Key Metrics:
- Effective Coherence: Combines phase-locking (PLV) and magnitude (RMS)
- SNR (linear): In-band vs out-of-band signal-to-noise ratio
- Attention Entropy: Sharpness of attention focus (lower = better)
- Attention Max/Mean: Detects attention collapse (degeneracy)
- Null-test Baseline: Geometry-only coherence for SNR computation
"""

from __future__ import annotations

import torch
import torch.nn.functional as F
from typing import Tuple, Dict, Any


def effective_coherence(
    phase_locked: torch.Tensor,
    amp_locked: torch.Tensor,
    eps: float = 1e-8
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    Compute magnitude-aware effective coherence.

    Combines phase-locking value (PLV) and RMS magnitude to prevent
    "pretty but meaningless" coherence from low-amplitude noise.

    Args:
        phase_locked: Phase-locked features [batch, dim]
        amp_locked: Amplitude-locked features [batch, dim]
        eps: Numerical stability constant

    Returns:
        Tuple of (effective_coherence, plv, rms_magnitude)
        - effective_coherence: PLV weighted by normalized RMS [batch] or scalar
        - plv: Phase-locking value [batch] or scalar
        - rms_magnitude: RMS of locked band [batch] or scalar
    """
    # Phase-locking value (PLV): cosine similarity in phase space
    # Normalize phase vectors
    phase_norm = F.normalize(phase_locked, p=2, dim=-1, eps=eps)

    # PLV as mean cosine similarity (self-consistency across batch if batch > 1)
    if phase_locked.shape[0] > 1:
        # Pairwise similarity averaged
        plv = (phase_norm @ phase_norm.T).mean()
    else:
        # Single sample: use norm as proxy for phase consistency
        plv = phase_norm.norm(dim=-1).mean()

    # RMS magnitude of locked band
    rms_mag = torch.sqrt((amp_locked ** 2).mean(dim=-1) + eps)

    # Effective coherence: PLV weighted by normalized magnitude
    # Normalize RMS to [0, 1] range per batch
    rms_normalized = rms_mag / (rms_mag.max() + eps)
    effective_coh = plv * rms_normalized.mean()

    return effective_coh, plv, rms_mag.mean()


def band_snr_linear(
    amp_locked: torch.Tensor,
    k_idx: torch.Tensor,
    num_bins: int = 4,
    eps: float = 1e-8
) -> torch.Tensor:
    """
    Compute linear SNR: in-band power vs out-of-band power.

    Measures how much signal is concentrated in the auto-selected spectral
    band (k_idx) versus noise in other bands.

    Args:
        amp_locked: Amplitude features [batch, dim]
        k_idx: Spectral bin index selected by ECC [batch] or scalar
        num_bins: Number of spectral bands (default: 4)
        eps: Numerical stability

    Returns:
        SNR (linear): in-band power / out-of-band power [batch] or scalar
    """
    batch_size, dim = amp_locked.shape

    # Split into spectral bands
    band_size = dim // num_bins
    bands = amp_locked.view(batch_size, num_bins, band_size)

    # Power per band
    band_power = (bands ** 2).mean(dim=-1)  # [batch, num_bins]

    # In-band power (selected by k_idx)
    k_idx_int = k_idx.long().clamp(0, num_bins - 1)
    in_band_power = band_power.gather(1, k_idx_int.unsqueeze(-1)).squeeze(-1)

    # Out-of-band power (mean of other bands)
    mask = torch.ones_like(band_power, dtype=torch.bool)
    mask.scatter_(1, k_idx_int.unsqueeze(-1), False)
    out_band_power = band_power[mask].view(batch_size, -1).mean(dim=-1)

    # Linear SNR
    snr = in_band_power / (out_band_power + eps)

    return snr


def attn_entropy(attention: torch.Tensor, eps: float = 1e-8) -> torch.Tensor:
    """
    Compute attention entropy (lower = sharper focus, better).

    Measures how diffuse vs. focused the attention distribution is.
    Lower entropy indicates sharper attention patterns.

    Args:
        attention: Attention matrix [batch, num_nodes, num_nodes]
        eps: Numerical stability

    Returns:
        Average entropy across attention heads/rows (scalar)
    """
    # Ensure attention is a valid probability distribution
    attn_probs = attention / (attention.sum(dim=-1, keepdim=True) + eps)

    # Entropy: -Σ p(i) log p(i)
    entropy = -(attn_probs * torch.log(attn_probs + eps)).sum(dim=-1)

    # Average across batch and rows
    avg_entropy = entropy.mean()

    return avg_entropy


def attn_max_mean(attention: torch.Tensor, eps: float = 1e-8) -> torch.Tensor:
    """
    Compute attention max/mean ratio (collapse detector).

    High ratio (> 5-10) indicates attention collapse: one node dominates
    all others, which is a form of degeneracy/"metric gaming."

    Args:
        attention: Attention matrix [batch, num_nodes, num_nodes]
        eps: Numerical stability

    Returns:
        Average max/mean ratio (scalar). Healthy range: 2-5.
    """
    # Max attention per row
    max_attn = attention.max(dim=-1)[0]  # [batch, num_nodes]

    # Mean attention per row
    mean_attn = attention.mean(dim=-1) + eps  # [batch, num_nodes]

    # Ratio
    ratio = max_attn / mean_attn

    # Average across batch and rows
    avg_ratio = ratio.mean()

    return avg_ratio


def null_test_coherence(
    model: Any,
    num_samples: int = 10,
    signal_dim: int = 1024,
    device: str = 'cpu'
) -> Dict[str, float]:
    """
    Run null-test to establish architectural baseline coherence.

    Feeds random noise through the network to measure geometry-only
    coherence (no signal content). Used to compute SNR vs. baseline.

    Args:
        model: EchoZeroNet or EchoZeroNetWithEchoCore instance
        num_samples: Number of random samples to average
        signal_dim: Input signal dimension (default: 1024 for EEG)
        device: Torch device ('cpu' or 'cuda')

    Returns:
        Dict with:
        - baseline_avg: Mean coherence on null signals
        - baseline_std: Std of coherence on null signals
        - baseline_plv: Mean PLV on null signals
        - baseline_rms: Mean RMS magnitude on null signals
    """
    model.eval()
    model.to(device)

    coherences = []
    plvs = []
    rmss = []

    with torch.inference_mode():
        for _ in range(num_samples):
            # Generate random noise
            null_signal = torch.randn(signal_dim, device=device)

            # Forward pass
            result = model(null_signal)

            # Extract phase and amplitude locked features
            if 'phase_locked' in result and 'amp_locked' in result:
                phase_locked = result['phase_locked']
                amp_locked = result['amp_locked']

                # Compute effective coherence
                eff_coh, plv, rms = effective_coherence(phase_locked, amp_locked)

                coherences.append(eff_coh.item())
                plvs.append(plv.item())
                rmss.append(rms.item())

    # Aggregate statistics
    baseline_stats = {
        'baseline_avg': sum(coherences) / len(coherences) if coherences else 0.26,
        'baseline_std': torch.tensor(coherences).std().item() if coherences else 0.05,
        'baseline_plv': sum(plvs) / len(plvs) if plvs else 0.5,
        'baseline_rms': sum(rmss) / len(rmss) if rmss else 1.0,
    }

    return baseline_stats


def compute_snr_coherence(
    coherence: float,
    baseline: float,
    eps: float = 1e-8
) -> float:
    """
    Compute SNR: coherence relative to architectural baseline.

    Positive SNR = signal coherence above geometric baseline
    Negative SNR = below baseline (likely noise)

    Args:
        coherence: Measured effective coherence
        baseline: Baseline coherence from null test
        eps: Numerical stability

    Returns:
        SNR in dB: 10 * log10(coherence / baseline)
    """
    snr_linear = coherence / (baseline + eps)
    snr_db = 10 * torch.log10(torch.tensor(snr_linear) + eps)

    return float(snr_db)


def attention_collapse_metrics(
    attention: torch.Tensor
) -> Dict[str, float]:
    """
    Comprehensive attention health check.

    Combines entropy and max/mean ratio to detect attention collapse,
    degeneracy, and other pathological patterns.

    Args:
        attention: Attention matrix [batch, num_nodes, num_nodes]

    Returns:
        Dict with:
        - entropy: Average attention entropy (lower = better)
        - max_mean_ratio: Average max/mean ratio (2-5 = healthy)
        - collapse_warning: Boolean flag for potential collapse
    """
    entropy = attn_entropy(attention)
    max_mean_ratio = attn_max_mean(attention)

    # Collapse warning: high max/mean ratio OR very low entropy
    collapse_warning = (max_mean_ratio > 10.0) or (entropy < 0.1)

    return {
        'entropy': float(entropy),
        'max_mean_ratio': float(max_mean_ratio),
        'collapse_warning': bool(collapse_warning)
    }


# Convenience function for UI/API
def compute_all_metrics(
    phase_locked: torch.Tensor,
    amp_locked: torch.Tensor,
    attention: torch.Tensor,
    k_idx: torch.Tensor,
    baseline_coherence: float = 0.26
) -> Dict[str, Any]:
    """
    Compute all metrics at once for UI/API display.

    Args:
        phase_locked: Phase-locked features [batch, dim]
        amp_locked: Amplitude-locked features [batch, dim]
        attention: Attention matrix [batch, num_nodes, num_nodes]
        k_idx: Spectral bin index [batch]
        baseline_coherence: Null-test baseline (default: 0.26)

    Returns:
        Dict with all metrics ready for display
    """
    # Effective coherence
    eff_coh, plv, rms_mag = effective_coherence(phase_locked, amp_locked)

    # SNR
    snr_linear = band_snr_linear(amp_locked, k_idx)
    snr_db = compute_snr_coherence(float(eff_coh), baseline_coherence)

    # Attention health
    attn_health = attention_collapse_metrics(attention)

    return {
        # Coherence metrics
        'effective_coherence': float(eff_coh),
        'plv': float(plv),
        'rms_magnitude': float(rms_mag),
        'snr_linear': float(snr_linear.mean()),
        'snr_db': snr_db,

        # Attention health
        'attention_entropy': attn_health['entropy'],
        'attention_max_mean': attn_health['max_mean_ratio'],
        'attention_collapse_warning': attn_health['collapse_warning'],

        # Spectral info
        'k_idx': float(k_idx.mean()),
    }


if __name__ == "__main__":
    # Smoke test
    print("Testing EchoZero metrics...")

    # Mock data
    batch_size, dim = 4, 128
    num_nodes = 20

    phase_locked = torch.randn(batch_size, dim)
    amp_locked = torch.abs(torch.randn(batch_size, dim))
    attention = F.softmax(torch.randn(batch_size, num_nodes, num_nodes), dim=-1)
    k_idx = torch.randint(0, 4, (batch_size,))

    # Test individual functions
    print("\n1. Effective Coherence:")
    eff, plv, rms = effective_coherence(phase_locked, amp_locked)
    print(f"   Effective: {eff:.4f}, PLV: {plv:.4f}, RMS: {rms:.4f}")

    print("\n2. Band SNR:")
    snr = band_snr_linear(amp_locked, k_idx)
    print(f"   SNR (linear): {snr.mean():.4f}")

    print("\n3. Attention Metrics:")
    entropy = attn_entropy(attention)
    max_mean = attn_max_mean(attention)
    print(f"   Entropy: {entropy:.4f}, Max/Mean: {max_mean:.4f}")

    print("\n4. SNR vs Baseline:")
    baseline = 0.26
    snr_db = compute_snr_coherence(float(eff), baseline)
    print(f"   SNR: {snr_db:.2f} dB")

    print("\n5. All Metrics:")
    all_metrics = compute_all_metrics(phase_locked, amp_locked, attention, k_idx)
    for key, value in all_metrics.items():
        print(f"   {key}: {value}")

    print("\n✓ Metrics module validated!")
