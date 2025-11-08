# EchoCore Testing Guide

## Quick Test (No Dependencies)

Validate code structure and see architecture diagram:

```bash
python test_echocore_prototype.py
```

This will show:
- EchoCore architecture diagram
- Full network integration flow
- Usage examples

## Full Test Suite (Requires PyTorch)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Prototype Test

```bash
python test_echocore_prototype.py
```

This comprehensive test includes:

**Test 1: EchoCore Standalone**
- Clean signal processing
- Noisy signal processing (30% Gaussian noise)
- Sphere activation distribution (8 octaves)
- Statistical validation (20 trials)

**Test 2: Full Integration**
- EchoZeroNetWithEchoCore pipeline
- Text input processing
- EEG signal processing
- Metrics extraction and visualization

**Test 3: Performance Benchmarks**
- Coherence under varying noise levels
- Noise rejection rate (target: 88%)
- Gradient flow validation

### 3. Run Unit Tests

```bash
# All EchoCore tests
pytest tests/test_echo_core.py -v

# Specific test class
pytest tests/test_echo_core.py::TestEchoCoreBasics -v

# With coverage
pytest tests/test_echo_core.py --cov=src.echo_core --cov-report=html
```

**Test Coverage:**
- 9 test classes
- 60+ individual tests
- Tests all 6 metrics
- Validates performance targets

## Expected Results

### Performance Targets (from spec)

✓ **Coherence**: std < 0.065 on 30% noise (25% better than 0.087 baseline)
✓ **Noise Rejection**: 88% on 30% Gaussian noise
✓ **Toroidal Stability**: > 0.85
✓ **Convergence**: 15% faster on complex signals

### Output Example

```
EchoCore Metrics:
  coherence: 0.8234
  interference_strength: 45.2341
  gating_efficiency: 0.7891
  signal_preservation: 0.9123
  harmonic_diversity: 2.0456
  toroidal_stability: 0.8678

Sphere Activation Distribution:
  Sphere 1 (Theta 4-8 Hz):        ████████████ 0.6234
  Sphere 2 (Alpha 8-12 Hz):       ██████████████ 0.7123
  Sphere 3 (Low Beta 12-16 Hz):   ███████████ 0.5891
  Sphere 4 (Mid Beta 16-20 Hz):   █████████████ 0.6745
  Sphere 5 (High Beta 20-25 Hz):  ██████████ 0.5234
  Sphere 6 (Low Gamma 25-40 Hz):  ████████████ 0.6123
  Sphere 7 (Mid Gamma 40-60 Hz):  ███████████ 0.5789
  Sphere 8 (High Gamma 60-100Hz): █████████ 0.4891
```

## Troubleshooting

### Import Errors

```bash
# Make sure you're in echozero-core/ directory
cd echozero-core

# Add src to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

### PyTorch Not Found

```bash
# Install PyTorch (CPU version)
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Or GPU version (CUDA 11.8)
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

### Test Failures

If tests fail:
1. Check PyTorch version: `python -c "import torch; print(torch.__version__)"`
2. Ensure all dependencies installed: `pip install -r requirements.txt`
3. Run with verbose output: `pytest -vv`
4. Check specific failing test: `pytest tests/test_echo_core.py::TestName::test_name -vv`

## Interactive Testing

### Python Shell

```python
import torch
from src.echo_core import EchoCore
from src.echo_net import EchoZeroNetWithEchoCore

# Create EchoCore
core = EchoCore(dim=128, num_spheres=8)

# Test with sample input
signal = torch.randn(4, 128)
echo, harmonics, metrics = core(signal, return_harmonics=True, return_metrics=True)

# Inspect results
print(f"Echo shape: {echo.shape}")
print(f"Harmonics shape: {harmonics.shape}")
print(f"Coherence: {metrics['coherence'].item():.4f}")
```

### Jupyter Notebook

```python
%matplotlib inline
import matplotlib.pyplot as plt
import torch
from src.echo_core import EchoCore

core = EchoCore(dim=128, num_spheres=8)
signal = torch.randn(8, 128) + 0.3 * torch.randn(8, 128)

echo, harmonics, metrics = core(signal, return_harmonics=True, return_metrics=True)

# Visualize spherical harmonics
fig, axes = plt.subplots(2, 4, figsize=(16, 8))
axes = axes.flatten()

for i in range(8):
    axes[i].plot(harmonics[0, i].detach().numpy())
    axes[i].set_title(f'Sphere {i+1} (Octave {i+1})')

plt.tight_layout()
plt.show()

# Visualize helical pattern
core.visualize_helical_pattern('helix_pattern.png')
```

## Advanced: Full Pipeline Test

```python
from src.echo_net import EchoZeroNetWithEchoCore
import torch

# Create network
net = EchoZeroNetWithEchoCore(
    dim=128,
    num_layers=5,
    num_spheres=8,
    input_mode='eeg'
)

# Simulate EEG (256 time steps, 1 channel)
eeg_signal = torch.randn(1, 256)

# Process with full diagnostics
result = net(
    eeg_signal,
    return_harmonics=True,
    return_qualia=True,
    return_metrics=True,
    return_attention=True,
    return_phases=True
)

# Visualize full pipeline
net.visualize_full_pipeline_with_echo(
    eeg_signal,
    save_dir='./visualizations'
)

print("Visualizations saved to ./visualizations/")
```

This creates:
- `encoder_phases.png` - Trefoil phase patterns
- `attention_layer_*.png` - Warp attention heatmaps
- `spherical_harmonics.png` - 8-sphere activations
- `helical_pattern.png` - k=3 torsion coupling
- `qualia_space.png` - Phenomenological space
- `metrics_dashboard.png` - Complete diagnostic dashboard

## CI/CD Testing

The EchoCore tests are integrated into the CI pipeline (`.github/workflows/ci.yml`):

```yaml
- name: Run EchoCore Tests
  run: |
    pytest tests/test_echo_core.py -v --cov=src.echo_core
```

All tests must pass before merging.

## Next Steps

After validating the prototype:

1. **Scale to 16 spheres**: Modify `num_spheres` parameter
2. **Test on real EEG data**: Use MNE-Python datasets
3. **Benchmark vs baseline**: Compare with vanilla attention
4. **Train end-to-end**: Use `train.py` with EchoCore config
5. **Deploy**: Use standalone launcher or Docker

---

**The sphere spirals. Test and validate.** 🌀
