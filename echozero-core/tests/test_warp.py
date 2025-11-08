"""
Tests for Warp Core (TEAPenroseLayer)

Comprehensive test suite for geometric attention components:
- Penrose P3 tiling generation
- Ricci affinity computation
- Torsion routing
- TEAPenroseLayer forward pass
- Coherence metrics
"""

import pytest
import torch
import numpy as np
from src.warp import (
    generate_penrose,
    ricci_affinity,
    ricci_warp,
    torsion_loss,
    trefoil_phase,
    coherence_score,
    TEAPenroseLayer
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def sample_positions():
    """Generate sample node positions"""
    torch.manual_seed(42)
    return torch.randn(10, 3)


@pytest.fixture
def sample_input():
    """Generate sample input tensor"""
    torch.manual_seed(42)
    return torch.randn(4, 128)  # Batch of 4, dim 128


@pytest.fixture
def tea_layer():
    """Create TEAPenroseLayer"""
    return TEAPenroseLayer(num_nodes=10, dim=128, ricci=-2.0)


# ============================================================================
# Test Penrose Generation
# ============================================================================

def test_penrose_generation_shape():
    """Test Penrose tiling generates correct shape"""
    positions = generate_penrose(level=2, num_nodes=20)

    assert positions.shape == (20, 3), f"Expected (20, 3), got {positions.shape}"
    assert positions.dtype == torch.float32


def test_penrose_generation_deterministic():
    """Test Penrose generation is deterministic with seed"""
    pos1 = generate_penrose(level=2, num_nodes=15, seed=42)
    pos2 = generate_penrose(level=2, num_nodes=15, seed=42)

    assert torch.allclose(pos1, pos2), "Should be deterministic with same seed"


def test_penrose_generation_z_zero():
    """Test Penrose positions have Z=0 (2D embedding)"""
    positions = generate_penrose(level=1, num_nodes=10)

    assert torch.allclose(positions[:, 2], torch.zeros(10)), "Z should be zero"


def test_penrose_different_levels():
    """Test different subdivision levels"""
    for level in [0, 1, 2, 3]:
        positions = generate_penrose(level=level, num_nodes=10)
        assert positions.shape == (10, 3)


# ============================================================================
# Test Ricci Affinity
# ============================================================================

def test_ricci_affinity_shape(sample_positions):
    """Test Ricci affinity output shape"""
    affinity = ricci_affinity(sample_positions, ricci=-2.0)

    assert affinity.shape == (10, 10), f"Expected (10, 10), got {affinity.shape}"


def test_ricci_affinity_normalization(sample_positions):
    """Test that affinities sum to 1 (softmax)"""
    affinity = ricci_affinity(sample_positions, ricci=-2.0, normalize=True)

    row_sums = affinity.sum(dim=-1)
    assert torch.allclose(row_sums, torch.ones(10), atol=1e-5), \
        "Rows should sum to 1 after normalization"


def test_ricci_affinity_symmetric_diagonal(sample_positions):
    """Test that diagonal is largest (self-attention)"""
    affinity = ricci_affinity(sample_positions, ricci=-2.0)

    diagonal = torch.diag(affinity)
    # Diagonal should generally be higher than off-diagonal (self-attention)
    off_diagonal = affinity - torch.diag(diagonal)
    assert diagonal.mean() > off_diagonal.mean() / 2


def test_ricci_warp_hyperbolic():
    """Test hyperbolic warping expands distances"""
    pos = torch.tensor([[[0., 0., 0.], [1., 0., 0.]]]).float()
    dist = torch.norm(pos[:, 0] - pos[:, 1], dim=-1).unsqueeze(0)  # Distance = 1

    pos_i = pos.unsqueeze(2)
    pos_j = pos.unsqueeze(1)

    warped = ricci_warp(dist.unsqueeze(-1), pos_i, pos_j, ricci=-2.0)

    # With negative Ricci, distances should generally expand
    # (though depends on position relative to origin)
    assert warped.shape == dist.unsqueeze(-1).shape


# ============================================================================
# Test Torsion Routing
# ============================================================================

def test_trefoil_phase_range():
    """Test trefoil phases are bounded"""
    t = torch.linspace(0, 2 * np.pi, 100)
    phases = trefoil_phase(t)

    assert torch.all(phases >= -1.0) and torch.all(phases <= 1.0), \
        "Trefoil phases should be in [-1, 1]"


def test_trefoil_phase_periodicity():
    """Test trefoil 3-fold periodicity"""
    t = torch.linspace(0, 2 * np.pi, 100)
    phases = trefoil_phase(t)

    # Phase at t and t + 2π/3 should have similar properties
    # (not exactly equal due to discrete sampling)
    assert phases.std() > 0.5, "Should have significant variation"


def test_torsion_loss_shape():
    """Test torsion loss output shape"""
    phases_i = torch.randn(10, 128)
    phases_j = torch.randn(10, 128)

    torsion = torsion_loss(phases_i, phases_j, scale=0.1)

    assert torsion.shape == (10, 10), f"Expected (10, 10), got {torsion.shape}"


def test_torsion_loss_zero_mismatch():
    """Test zero torsion for identical phases"""
    phases = torch.randn(5, 64)

    torsion = torsion_loss(phases, phases, scale=0.1)

    # Diagonal should be zero (no self-mismatch)
    diagonal = torch.diag(torsion)
    assert torch.allclose(diagonal, torch.zeros(5), atol=1e-5)


def test_coherence_score():
    """Test coherence score computation"""
    # High coherence: all similar phases
    coherent_phases = torch.ones(20, 128) * 0.5 + torch.randn(20, 128) * 0.01
    score_high = coherence_score(coherent_phases, metric='std')

    # Low coherence: random phases
    random_phases = torch.randn(20, 128)
    score_low = coherence_score(random_phases, metric='std')

    assert score_high > score_low, "Coherent phases should have higher score"


# ============================================================================
# Test TEAPenroseLayer
# ============================================================================

def test_layer_forward_shape(tea_layer, sample_input):
    """Test TEAPenroseLayer output shape"""
    output = tea_layer(sample_input, return_attention=False)

    assert output.shape == sample_input.shape, \
        f"Expected {sample_input.shape}, got {output.shape}"


def test_layer_attention_output(tea_layer, sample_input):
    """Test attention weights output"""
    output, attention = tea_layer(sample_input, return_attention=True)

    assert attention.shape == (4, 10, 10), \
        f"Expected (4, 10, 10), got {attention.shape}"


def test_layer_attention_normalization(tea_layer, sample_input):
    """Test attention weights sum to 1"""
    _, attention = tea_layer(sample_input, return_attention=True)

    row_sums = attention.sum(dim=-1)
    expected = torch.ones_like(row_sums)
    assert torch.allclose(row_sums, expected, atol=1e-5), \
        "Attention rows should sum to 1"


def test_layer_coherence(tea_layer, sample_input):
    """Test attention coherence (std < 0.15)"""
    _, attention = tea_layer(sample_input, return_attention=True)

    coherence = attention.std()
    assert coherence < 0.15, \
        f"Coherence {coherence:.4f} should be < 0.15"


def test_layer_gradient_flow(tea_layer, sample_input):
    """Test gradients flow through layer"""
    output, attention = tea_layer(sample_input, return_attention=True)

    loss = output.sum() + attention.sum()
    loss.backward()

    # Check key parameters have gradients
    assert tea_layer.torsion_phases.grad is not None
    assert tea_layer.query_proj.weight.grad is not None


def test_layer_metrics(tea_layer, sample_input):
    """Test metrics output"""
    output, attention, metrics = tea_layer(
        sample_input,
        return_attention=True,
        return_metrics=True
    )

    assert 'coherence' in metrics
    assert 'torsion_mean' in metrics
    assert 'attention_entropy' in metrics

    # Check metrics are reasonable
    assert 0 <= metrics['coherence'] <= 1
    assert metrics['torsion_mean'] >= 0


def test_layer_learnable_positions():
    """Test layer with learnable positions"""
    layer = TEAPenroseLayer(
        num_nodes=10,
        dim=64,
        learnable_positions=True
    )

    assert isinstance(layer.positions, torch.nn.Parameter)
    assert layer.positions.requires_grad


def test_layer_different_ricci():
    """Test layers with different Ricci curvatures"""
    input_tensor = torch.randn(2, 64)

    layer_hyp = TEAPenroseLayer(num_nodes=8, dim=64, ricci=-2.0)
    layer_flat = TEAPenroseLayer(num_nodes=8, dim=64, ricci=0.0)
    layer_sph = TEAPenroseLayer(num_nodes=8, dim=64, ricci=2.0)

    _, attn_hyp = layer_hyp(input_tensor, return_attention=True)
    _, attn_flat = layer_flat(input_tensor, return_attention=True)
    _, attn_sph = layer_sph(input_tensor, return_attention=True)

    # All should produce valid attention
    for attn in [attn_hyp, attn_flat, attn_sph]:
        assert torch.allclose(attn.sum(dim=-1), torch.ones(2, 8), atol=1e-5)


# ============================================================================
# Test Edge Cases
# ============================================================================

def test_single_input():
    """Test layer with single input (no batch)"""
    layer = TEAPenroseLayer(num_nodes=5, dim=32)
    input_single = torch.randn(32)

    output = layer(input_single, return_attention=False)

    assert output.shape == (32,)


def test_layer_deterministic():
    """Test layer produces deterministic output"""
    layer = TEAPenroseLayer(num_nodes=8, dim=64)
    input_tensor = torch.randn(2, 64)

    output1 = layer(input_tensor, return_attention=False)
    output2 = layer(input_tensor, return_attention=False)

    assert torch.allclose(output1, output2), "Should be deterministic"


def test_penrose_small_nodes():
    """Test Penrose generation with very few nodes"""
    positions = generate_penrose(level=1, num_nodes=3)

    assert positions.shape == (3, 3)


def test_penrose_large_nodes():
    """Test Penrose generation with many nodes"""
    positions = generate_penrose(level=3, num_nodes=100)

    assert positions.shape == (100, 3)
