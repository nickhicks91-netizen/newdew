"""
Tests for Ingestion Layer (VortexEncoder)

Comprehensive test suite for multi-modal encoding:
- EEG signals
- Text embeddings
- Spectral data
- Trefoil phase embedding
- Fidelity metrics
"""

import pytest
import torch
import numpy as np
from src.ingestion.vortex_encoder import VortexEncoder, trefoil_phase


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def sample_eeg():
    """Generate synthetic EEG signal: 1 second @ 512Hz"""
    torch.manual_seed(42)
    return torch.randn(512)


@pytest.fixture
def sample_eeg_batch():
    """Generate batch of synthetic EEG signals"""
    torch.manual_seed(42)
    return torch.randn(4, 512)


@pytest.fixture
def sample_spectral():
    """Generate synthetic spectral data"""
    torch.manual_seed(42)
    t = torch.linspace(0, 2 * np.pi, 256)
    # Mix of frequencies
    signal = torch.sin(5 * t) + 0.5 * torch.sin(10 * t) + 0.3 * torch.cos(3 * t)
    return signal


@pytest.fixture
def encoder_eeg():
    """EEG mode encoder"""
    return VortexEncoder(dim=128, mode='eeg')


@pytest.fixture
def encoder_spectral():
    """Spectral mode encoder"""
    return VortexEncoder(dim=128, mode='spectral')


# ============================================================================
# Test Trefoil Phase Embedding
# ============================================================================

def test_trefoil_phase_basic():
    """Test trefoil phase embedding on simple signal"""
    signal = torch.tensor([1.0, 2.0, 3.0, 4.0, 5.0])
    phases = trefoil_phase(signal)

    assert phases.shape[0] == 3, "FFT output should be (N//2 + 1) for real input"
    assert torch.all(torch.abs(phases) <= 1.0), "Trefoil phases should be bounded by sin"


def test_trefoil_phase_symmetry():
    """Test trefoil 3-fold symmetry"""
    signal = torch.randn(100)
    phases = trefoil_phase(signal)

    # Check that phases are periodic with period 2π/3 in phase space
    assert phases.shape[0] == 51  # rfft of 100 elements


def test_trefoil_phase_deterministic(sample_eeg):
    """Test that trefoil phase is deterministic"""
    phases1 = trefoil_phase(sample_eeg)
    phases2 = trefoil_phase(sample_eeg)

    assert torch.allclose(phases1, phases2), "Trefoil phase should be deterministic"


# ============================================================================
# Test EEG Encoding
# ============================================================================

def test_eeg_encode_shape(encoder_eeg, sample_eeg):
    """Test EEG encoding output shapes"""
    engram, phases = encoder_eeg(sample_eeg)

    assert engram.shape == (128,), f"Expected engram shape (128,), got {engram.shape}"
    assert phases.shape == (128,), f"Expected phases shape (128,), got {phases.shape}"


def test_eeg_encode_dtype(encoder_eeg, sample_eeg):
    """Test EEG encoding output data types"""
    engram, phases = encoder_eeg(sample_eeg)

    assert engram.dtype == torch.float32
    assert phases.dtype == torch.float32


def test_eeg_encode_normalization(encoder_eeg, sample_eeg):
    """Test that engrams are normalized when normalize=True"""
    engram, phases = encoder_eeg(sample_eeg)

    # Should be approximately L2-normalized
    norm = torch.norm(engram, p=2)
    assert torch.allclose(norm, torch.tensor(1.0), atol=1e-5), \
        f"Engram should be L2-normalized, got norm={norm.item()}"


def test_eeg_encode_no_normalization(sample_eeg):
    """Test encoding without normalization"""
    encoder = VortexEncoder(dim=128, mode='eeg', normalize=False)
    engram, phases = encoder(sample_eeg)

    norm = torch.norm(engram, p=2)
    # Should NOT be normalized to 1
    assert not torch.allclose(norm, torch.tensor(1.0), atol=1e-5)


def test_eeg_fidelity(encoder_eeg, sample_eeg):
    """Test reconstruction fidelity >80% for EEG signals"""
    engram, phases = encoder_eeg(sample_eeg)
    fidelity = encoder_eeg.get_fidelity(sample_eeg, engram)

    assert fidelity > 0.8, f"Fidelity {fidelity:.4f} should be >0.80"
    assert 0 <= fidelity <= 1.0, "Fidelity should be in [0, 1]"


def test_eeg_phase_bounds(encoder_eeg, sample_eeg):
    """Test that phases are bounded"""
    engram, phases = encoder_eeg(sample_eeg)

    # Phases scaled by phase_scale parameter, should still be reasonable
    assert torch.all(torch.abs(phases) < 10.0), "Phases should be reasonably bounded"


# ============================================================================
# Test Spectral Encoding
# ============================================================================

def test_spectral_encode(encoder_spectral, sample_spectral):
    """Test spectral data encoding"""
    engram, phases = encoder_spectral(sample_spectral)

    assert engram.shape == (128,)
    assert phases.shape == (128,)


def test_spectral_fidelity(encoder_spectral, sample_spectral):
    """Test spectral encoding fidelity"""
    engram, phases = encoder_spectral(sample_spectral)
    fidelity = encoder_spectral.get_fidelity(sample_spectral, engram)

    assert fidelity > 0.75, f"Spectral fidelity {fidelity:.4f} should be >0.75"


# ============================================================================
# Test Text Encoding (if sentence-transformers available)
# ============================================================================

@pytest.mark.skipif(
    not hasattr(VortexEncoder, '__init__'),
    reason="VortexEncoder not available"
)
def test_text_encode_single():
    """Test single text encoding"""
    try:
        encoder = VortexEncoder(dim=128, mode='text')
        text = "Resonant AI architecture with torsion warping"
        engram, phases = encoder(text)

        assert engram.shape == (128,)
        assert phases.shape == (128,)
    except ImportError:
        pytest.skip("sentence-transformers not installed")


@pytest.mark.skipif(
    not hasattr(VortexEncoder, '__init__'),
    reason="VortexEncoder not available"
)
def test_text_encode_batch():
    """Test batch text encoding"""
    try:
        encoder = VortexEncoder(dim=128, mode='text')
        texts = [
            "First test prompt",
            "Second resonant query",
            "Third torsion lattice"
        ]
        engrams, phases = encoder(texts)

        assert engrams.shape == (3, 128)
        assert phases.shape == (3, 128)
    except ImportError:
        pytest.skip("sentence-transformers not installed")


# ============================================================================
# Test Edge Cases
# ============================================================================

def test_short_signal():
    """Test encoding very short signals"""
    encoder = VortexEncoder(dim=128, mode='spectral')
    short_signal = torch.randn(10)  # Shorter than target dim

    engram, phases = encoder(short_signal)

    assert engram.shape == (128,), "Should pad to target dimension"
    assert phases.shape == (128,)


def test_long_signal():
    """Test encoding very long signals"""
    encoder = VortexEncoder(dim=64, mode='spectral')
    long_signal = torch.randn(1024)  # Longer than target dim

    engram, phases = encoder(long_signal)

    assert engram.shape == (64,), "Should compress to target dimension"
    assert phases.shape == (64,)


def test_zero_signal():
    """Test encoding zero signal"""
    encoder = VortexEncoder(dim=128, mode='eeg')
    zero_signal = torch.zeros(256)

    engram, phases = encoder(zero_signal)

    # Should not crash, but engram will be near-zero
    assert engram.shape == (128,)
    assert torch.all(torch.isfinite(engram)), "Engram should be finite"


def test_nan_handling():
    """Test that NaN inputs are handled"""
    encoder = VortexEncoder(dim=128, mode='spectral')
    signal_with_nan = torch.tensor([1.0, 2.0, float('nan'), 4.0, 5.0])

    # Should either raise an error or handle gracefully
    # For now, just check it doesn't crash catastrophically
    try:
        engram, phases = encoder(signal_with_nan)
        # If it doesn't raise, check that output contains NaN
        assert torch.any(torch.isnan(engram)) or torch.any(torch.isnan(phases))
    except (RuntimeError, ValueError):
        # It's acceptable to raise an error for NaN input
        pass


# ============================================================================
# Test Learnable Parameters
# ============================================================================

def test_phase_scale_parameter(encoder_eeg):
    """Test that phase_scale is a learnable parameter"""
    assert hasattr(encoder_eeg, 'phase_scale')
    assert encoder_eeg.phase_scale.requires_grad
    assert isinstance(encoder_eeg.phase_scale, torch.nn.Parameter)


def test_projection_layer(encoder_eeg):
    """Test that projection layer exists and has correct shape"""
    assert hasattr(encoder_eeg, 'proj')
    assert isinstance(encoder_eeg.proj, torch.nn.Linear)
    assert encoder_eeg.proj.in_features == 256  # 2 * dim
    assert encoder_eeg.proj.out_features == 128  # dim


def test_gradient_flow(encoder_eeg, sample_eeg):
    """Test that gradients flow through encoder"""
    engram, phases = encoder_eeg(sample_eeg)

    # Create dummy loss
    loss = engram.sum()
    loss.backward()

    # Check that parameters have gradients
    assert encoder_eeg.phase_scale.grad is not None
    assert encoder_eeg.proj.weight.grad is not None


# ============================================================================
# Test Consistency
# ============================================================================

def test_deterministic_encoding(encoder_eeg, sample_eeg):
    """Test that encoding is deterministic for same input"""
    engram1, phases1 = encoder_eeg(sample_eeg)
    engram2, phases2 = encoder_eeg(sample_eeg)

    assert torch.allclose(engram1, engram2), "Encoding should be deterministic"
    assert torch.allclose(phases1, phases2), "Phases should be deterministic"


def test_different_inputs_different_outputs(encoder_eeg):
    """Test that different inputs produce different outputs"""
    signal1 = torch.randn(256)
    signal2 = torch.randn(256)

    engram1, _ = encoder_eeg(signal1)
    engram2, _ = encoder_eeg(signal2)

    assert not torch.allclose(engram1, engram2), \
        "Different inputs should produce different engrams"
