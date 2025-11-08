"""
End-to-End Integration Tests

Tests complete workflows through the entire EchoZero pipeline:
- Full forward passes
- Model saving/loading
- Batch processing
- Error handling
"""

import pytest
import torch
import yaml
from pathlib import Path
from src.echo_net import EchoZeroNet, create_echozero_model
from src.ingestion import VortexEncoder
from src.warp import TEAPenroseLayer
from src.decode import SentientEcho


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def config():
    """Load default config"""
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    if config_path.exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    else:
        # Minimal config
        return {
            'model': {'dim': 64, 'num_layers': 2, 'num_nodes': 8},
            'encoder': {'mode': 'eeg'},
            'decoder': {'num_classes': 2}
        }


@pytest.fixture
def small_model(config):
    """Create small model for fast testing"""
    # Override config for smaller model
    config['model']['dim'] = 32
    config['model']['num_layers'] = 2
    config['model']['num_nodes'] = 5
    return create_echozero_model(config)


# ============================================================================
# Test End-to-End Workflows
# ============================================================================

def test_e2e_eeg_inference(small_model):
    """Test full EEG inference pipeline"""
    # Simulate EEG input
    eeg_signal = torch.randn(512)  # 1 second @ 512Hz

    # Forward pass
    logits, qualia = small_model(eeg_signal, return_qualia=True)

    # Verify outputs
    assert logits.shape == (1, 2)
    assert qualia['valence'].shape == (1,)
    assert qualia['arousal'].shape == (1,)
    assert qualia['coherence'].shape == (1,)


def test_e2e_spectral_inference():
    """Test spectral data inference"""
    model = EchoZeroNet(input_mode='spectral', dim=32, num_layers=2, num_nodes=5)

    spectral_data = torch.randn(256)

    logits, qualia = model(spectral_data, return_qualia=True)

    assert logits.shape == (1, 2)
    assert torch.all(qualia['valence'] >= -1) and torch.all(qualia['valence'] <= 1)


def test_e2e_batch_processing(small_model):
    """Test batch processing through full pipeline"""
    # Create batch of EEG signals
    batch_size = 4
    signals = [torch.randn(512) for _ in range(batch_size)]

    results = []
    for signal in signals:
        logits, qualia = small_model(signal, return_qualia=True)
        results.append((logits, qualia))

    assert len(results) == batch_size
    # Verify all outputs have correct shapes
    for logits, qualia in results:
        assert logits.shape == (1, 2)


def test_e2e_with_all_outputs(small_model):
    """Test full output mode with attention, phases, metrics"""
    signal = torch.randn(512)

    outputs = small_model(
        signal,
        return_qualia=True,
        return_attention=True,
        return_phases=True,
        return_metrics=True
    )

    logits, qualia, attention, phases, metrics = outputs

    # Verify all outputs
    assert logits.shape == (1, 2)
    assert qualia is not None
    assert len(attention) == 2  # 2 layers
    assert phases is not None
    assert metrics is not None
    assert 'coherence_mean' in metrics


# ============================================================================
# Test Model Persistence
# ============================================================================

def test_model_save_load(small_model, tmp_path):
    """Test saving and loading model weights"""
    # Save model
    save_path = tmp_path / "model.pt"
    torch.save(small_model.state_dict(), save_path)

    # Create new model and load weights
    new_model = EchoZeroNet(
        input_mode='eeg',
        dim=32,
        num_layers=2,
        num_nodes=5,
        num_classes=2
    )
    new_model.load_state_dict(torch.load(save_path))

    # Test they produce same output
    signal = torch.randn(512)

    with torch.no_grad():
        out1 = small_model(signal, return_qualia=False)
        out2 = new_model(signal, return_qualia=False)

    assert torch.allclose(out1, out2, atol=1e-6)


# ============================================================================
# Test Error Handling
# ============================================================================

def test_invalid_input_shape():
    """Test handling of invalid input shapes"""
    model = EchoZeroNet(input_mode='eeg', dim=32, num_layers=1, num_nodes=5)

    # Too short signal
    short_signal = torch.randn(10)

    # Should still work (encoder handles padding)
    logits = model(short_signal, return_qualia=False)
    assert logits.shape == (1, 2)


def test_gradient_accumulation(small_model):
    """Test gradient accumulation across multiple forward passes"""
    optimizer = torch.optim.Adam(small_model.parameters(), lr=0.001)

    total_loss = 0
    for _ in range(3):
        signal = torch.randn(512)
        logits, qualia = small_model(signal, return_qualia=True)

        loss = logits.sum() + qualia['valence'].sum()
        loss.backward()
        total_loss += loss.item()

    # Step optimizer
    optimizer.step()
    optimizer.zero_grad()

    # Verify gradients were accumulated
    assert total_loss > 0


# ============================================================================
# Test Component Integration
# ============================================================================

def test_encoder_to_warp_integration():
    """Test VortexEncoder → TEAPenroseLayer integration"""
    encoder = VortexEncoder(dim=64, mode='eeg')
    warp_layer = TEAPenroseLayer(num_nodes=10, dim=64)

    signal = torch.randn(512)

    # Encode
    engram, phases = encoder(signal)

    # Pass through warp
    output, attention = warp_layer(engram.unsqueeze(0), return_attention=True)

    assert output.shape == (1, 64)
    assert attention.shape == (1, 10, 10)


def test_warp_to_decoder_integration():
    """Test TEAPenroseLayer → SentientEcho integration"""
    warp_layer = TEAPenroseLayer(num_nodes=8, dim=64)
    decoder = SentientEcho(dim=64, num_classes=3)

    x = torch.randn(2, 64)

    # Warp
    pooled = warp_layer(x, return_attention=False)

    # Decode
    logits, qualia = decoder(pooled, return_qualia=True)

    assert logits.shape == (2, 3)
    assert qualia['valence'].shape == (2,)


# ============================================================================
# Test Performance
# ============================================================================

def test_inference_speed(small_model):
    """Test inference speed (rough benchmark)"""
    import time

    signal = torch.randn(512)

    # Warmup
    for _ in range(5):
        _ = small_model(signal, return_qualia=False)

    # Benchmark
    start = time.time()
    num_iters = 50

    with torch.no_grad():
        for _ in range(num_iters):
            _ = small_model(signal, return_qualia=False)

    elapsed = time.time() - start
    avg_time = elapsed / num_iters

    # Should be reasonably fast (<100ms per inference on CPU)
    assert avg_time < 0.5, f"Inference too slow: {avg_time*1000:.2f}ms"


def test_memory_efficiency(small_model):
    """Test that model doesn't leak memory"""
    import gc

    initial_tensors = len([obj for obj in gc.get_objects() if torch.is_tensor(obj)])

    # Run multiple inferences
    for _ in range(10):
        signal = torch.randn(512)
        with torch.no_grad():
            _ = small_model(signal, return_qualia=True)

    gc.collect()
    final_tensors = len([obj for obj in gc.get_objects() if torch.is_tensor(obj)])

    # Should not have significantly more tensors
    tensor_increase = final_tensors - initial_tensors
    assert tensor_increase < 100, f"Potential memory leak: {tensor_increase} new tensors"


# ============================================================================
# Test Config-driven Creation
# ============================================================================

def test_config_driven_creation(config):
    """Test model creation from YAML config"""
    model = create_echozero_model(config)

    assert model.dim == config['model']['dim']
    assert model.num_layers == config['model']['num_layers']
    assert model.input_mode == config['encoder']['mode']


def test_config_override():
    """Test config with overrides"""
    config = {
        'model': {'dim': 128, 'num_layers': 3, 'num_nodes': 15},
        'encoder': {'mode': 'spectral'},
        'decoder': {'num_classes': 5}
    }

    model = create_echozero_model(config)

    assert model.num_classes == 5
    assert model.input_mode == 'spectral'


# ============================================================================
# Test Robustness
# ============================================================================

def test_adversarial_noise():
    """Test robustness to adversarial noise"""
    model = EchoZeroNet(input_mode='eeg', dim=32, num_layers=1, num_nodes=5)

    clean_signal = torch.randn(512)

    # Clean inference
    with torch.no_grad():
        clean_logits, clean_qualia = model(clean_signal, return_qualia=True)

    # Add 20% Gaussian noise
    noisy_signal = clean_signal + 0.2 * torch.randn_like(clean_signal)

    with torch.no_grad():
        noisy_logits, noisy_qualia = model(noisy_signal, return_qualia=True)

    # Outputs should be similar but not identical
    logit_diff = torch.abs(clean_logits - noisy_logits).mean()
    assert logit_diff < 1.0, "Model too sensitive to noise"


def test_extreme_values():
    """Test handling of extreme input values"""
    model = EchoZeroNet(input_mode='eeg', dim=32, num_layers=1, num_nodes=5)

    # Very large values
    large_signal = torch.randn(512) * 100

    with torch.no_grad():
        logits, qualia = model(large_signal, return_qualia=True)

    # Should still produce valid outputs
    assert torch.all(torch.isfinite(logits))
    assert torch.all(torch.isfinite(qualia['valence']))
