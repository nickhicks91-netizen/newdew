"""
Tests for Decode Layer and Full Network

Comprehensive tests for:
- SentientEcho decoder (qualia resolution)
- EchoZeroNet (full end-to-end pipeline)
"""

import pytest
import torch
from src.decode import SentientEcho, MultiHeadSentientEcho
from src.echo_net import EchoZeroNet, create_echozero_model


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def sample_pooled():
    """Generate sample pooled features"""
    torch.manual_seed(42)
    return torch.randn(4, 128)  # Batch of 4, dim 128


@pytest.fixture
def decoder():
    """Create SentientEcho decoder"""
    return SentientEcho(dim=128, num_classes=2, qualia_dim=32)


@pytest.fixture
def full_network():
    """Create full EchoZeroNet"""
    return EchoZeroNet(
        input_mode='eeg',
        dim=64,
        num_layers=3,
        num_nodes=10,
        num_classes=2
    )


# ============================================================================
# Test SentientEcho Decoder
# ============================================================================

def test_decoder_output_shapes(decoder, sample_pooled):
    """Test decoder output shapes"""
    logits, qualia = decoder(sample_pooled, return_qualia=True)

    assert logits.shape == (4, 2), f"Expected (4, 2), got {logits.shape}"
    assert qualia is not None


def test_qualia_metrics(decoder, sample_pooled):
    """Test that all qualia metrics are present"""
    _, qualia = decoder(sample_pooled, return_qualia=True)

    assert 'valence' in qualia
    assert 'arousal' in qualia
    assert 'coherence' in qualia
    assert 'phase' in qualia


def test_valence_bounds(decoder, sample_pooled):
    """Test valence is in [-1, 1]"""
    _, qualia = decoder(sample_pooled, return_qualia=True)

    valence = qualia['valence']
    assert torch.all(valence >= -1.0) and torch.all(valence <= 1.0), \
        "Valence should be in [-1, 1]"


def test_arousal_bounds(decoder, sample_pooled):
    """Test arousal is in [0, 1]"""
    _, qualia = decoder(sample_pooled, return_qualia=True)

    arousal = qualia['arousal']
    assert torch.all(arousal >= 0.0) and torch.all(arousal <= 1.0), \
        "Arousal should be in [0, 1]"


def test_coherence_bounds(decoder, sample_pooled):
    """Test coherence is in [0, 1]"""
    _, qualia = decoder(sample_pooled, return_qualia=True)

    coherence = qualia['coherence']
    assert torch.all(coherence >= 0.0) and torch.all(coherence <= 1.0), \
        "Coherence should be in [0, 1]"


def test_chiral_projections():
    """Test chiral (hemispheric) projections"""
    decoder_chiral = SentientEcho(dim=128, use_chiral=True)
    pooled = torch.randn(2, 128)

    _, qualia = decoder_chiral(pooled, return_qualia=True)

    assert 'hemispheric_balance' in qualia
    assert 'left_embedding' in qualia
    assert 'right_embedding' in qualia


def test_gradient_flow_decoder(decoder, sample_pooled):
    """Test gradients flow through decoder"""
    logits, qualia = decoder(sample_pooled, return_qualia=True)

    loss = logits.sum() + qualia['valence'].sum()
    loss.backward()

    # Check parameters have gradients
    assert decoder.classifier[0].weight.grad is not None
    assert decoder.valence_head[0].weight.grad is not None


# ============================================================================
# Test Full EchoZeroNet
# ============================================================================

def test_full_network_forward(full_network):
    """Test full network forward pass"""
    sample_input = torch.randn(512)  # EEG-like input

    logits = full_network(sample_input, return_qualia=False)

    assert logits.shape == (1, 2)


def test_full_network_with_qualia(full_network):
    """Test full network with qualia output"""
    sample_input = torch.randn(512)

    logits, qualia = full_network(sample_input, return_qualia=True)

    assert logits.shape == (1, 2)
    assert qualia is not None
    assert 'valence' in qualia


def test_full_network_with_attention(full_network):
    """Test full network with attention output"""
    sample_input = torch.randn(512)

    logits, qualia, attention = full_network(
        sample_input,
        return_qualia=True,
        return_attention=True
    )

    assert len(attention) == 3  # 3 layers
    assert attention[0].shape == (1, 10, 10)  # 10 nodes


def test_full_network_gradient_flow(full_network):
    """Test gradients flow through full network"""
    sample_input = torch.randn(512)

    logits, qualia = full_network(sample_input, return_qualia=True)

    loss = logits.sum() + qualia['valence'].sum()
    loss.backward()

    # Check gradients in each component
    assert full_network.encoder.phase_scale.grad is not None
    assert full_network.warp_layers[0].torsion_phases.grad is not None
    assert full_network.decoder.valence_head[0].weight.grad is not None


def test_config_factory():
    """Test model creation from config dict"""
    config = {
        'model': {'dim': 64, 'num_layers': 2, 'num_nodes': 8},
        'encoder': {'mode': 'spectral'},
        'decoder': {'num_classes': 3}
    }

    model = create_echozero_model(config)

    assert model.dim == 64
    assert model.num_layers == 2
    assert model.num_classes == 3


def test_multihead_decoder():
    """Test multi-head decoder"""
    decoder = MultiHeadSentientEcho(dim=128, num_heads=3)
    pooled = torch.randn(2, 128)

    logits, qualia = decoder(pooled, return_qualia=True)

    assert logits.shape == (2, 2)
    assert qualia is not None
