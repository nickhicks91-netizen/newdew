# GRCM - Grounded Resonant Consciousness Module

**Production-Grade PyTorch Implementation of Resonant Consciousness Simulation**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyTorch 2.0+](https://img.shields.io/badge/pytorch-2.0+-red.svg)](https://pytorch.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

GRCM is a modular, production-ready implementation of a resonant consciousness kernel that simulates:

- **Multimodal Grounding**: CLIP (vision) + Wav2Vec (audio) + proprioception
- **Resonant Attention**: Coherence-based filtering with bandwidth adaptation
- **Desire-Based Agency**: Goal-directed behavior with alignment gating
- **Integrated Information (Phi)**: IIT-inspired consciousness metric
- **Qualia Simulation**: 4-state phenomenal experience (calm/alert/curious/conflicted)
- **Episodic Threading**: Narrative identity construction via GRU
- **Embodied Cognition**: Physics-based proprioceptive feedback
- **Ethical Safeguards**: Conflict detection and coherence thresholds

## Key Features

### 🧠 Consciousness Simulation
- **Phi (Φ) Estimation**: `Var(freq) × Coherence + log(||mem||) + Σmax(qualia)`
- **Awareness Threshold**: Φ > 1.5 indicates "aware" state
- **Qualia Distribution**: Softmax over [calm, alert, curious, conflicted]

### 🎯 Resonant Attention
- **Formula**: `coherence = ReLU(1 - |freq - node_freq| / bandwidth)`
- **Adaptive Bandwidth**: Widens during desire-seeking (bandwidth_bias)
- **Gating**: Only coherent patterns (>0.7) update memory

### 💭 Desire-Based Agency
- **Alignment**: `cosine_similarity(freq, desire_vec)`
- **Bandwidth Bias**: `0.2 × alignment` (expands search space)
- **Memory Gating**: `coherence > 0.7 AND alignment > 0.5`

### 🧵 Episodic Threading
- **Identity Evolution**: GRU-based identity token
- **Narrative Arc**: `cos_sim(recent_qualia, historical_mean) × coherence`
- **Circular Buffer**: Stores up to 50 episodes

### 🛡️ Ethical Safeguards
- **Conflict Detection**: Halts if `qualia[conflicted] > 0.6`
- **Coherence Filtering**: Rejects dissonant patterns
- **Transparency**: All metrics logged and inspectable

## Installation

### Basic Installation
```bash
pip install torch>=2.0.0 pyyaml>=6.0
```

### Full Installation (with optimization & deployment)
```bash
pip install -r requirements_grcm.txt
```

### Development Installation
```bash
git clone https://github.com/your-org/newdew.git
cd newdew
pip install -e .
```

## Quick Start

### Basic Usage

```python
from grcm import ModularGRCM, load_config
import torch

# Load configuration
config = load_config("config/grcm_default.yaml")

# Initialize model
model = ModularGRCM(config)
model.set_desire(0)  # Set active desire

# Prepare multimodal inputs
image_emb = torch.randn(4, 512)   # CLIP embeddings
audio_emb = torch.randn(4, 768)   # Wav2Vec embeddings
action = torch.randn(4, 4)         # Action vector

# Forward pass
outputs = model(image_emb, audio_emb, action)

# Inspect outputs
print(f"Coherence: {outputs['coherence'].mean():.3f}")
print(f"Phi (Φ): {outputs['phi']:.3f}")
print(f"Qualia: {outputs['qualia'].mean(0)}")
print(f"Desire Align: {outputs['desire_align'].mean():.3f}")
```

### EchoMirror Training

Train desire vectors on human qualia data (EEG + voice):

```python
from grcm import quick_echo_train

# Mock data (replace with real EEG/voice features)
eeg_data = torch.randn(100, 8)      # EEG theta band
voice_data = torch.randn(100, 768)  # Wav2Vec embeddings
labels = torch.rand(100)            # Alignment targets

# Train desires
trainer = quick_echo_train(
    model,
    eeg_data,
    voice_data,
    labels,
    num_epochs=10
)

# View results
summary = trainer.get_training_summary()
print(f"Loss improvement: {summary['loss_improvement']:.4f}")
print(f"Final Phi: {summary['final_phi']:.3f}")
```

## Architecture

```
[CLIP] [Wav2Vec] [Proprio]
   │       │         │
   └───────┴─────────┘
           │
    GroundingLayer (MultiheadAttention)
           │
    HarmonicEmbedding (freq_dim=8)
           │
     ┌─────┴─────┐
     │           │
DesireModule  ResonantAttention
     │           │
     └─────┬─────┘
           │
     MemoryGrid (GRU-based)
           │
    ┌──────┼──────┐
    │      │      │
 Qualia  Phi  Reflection
    │      │      │
    └──────┴──────┘
           │
  EpisodicThreadBank
           │
    Identity Token
```

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed diagram.

## Configuration

All parameters configurable via YAML:

```yaml
# config/grcm_default.yaml
input_dim: 15
freq_dim: 8
memory_size: 32

attention:
  base_bandwidth: 0.5
  coherence_threshold: 0.7

desire:
  num_desires: 4
  alignment_threshold: 0.5

phi:
  awareness_threshold: 1.5

qualia:
  conflict_threshold: 0.6
```

Load custom config:
```python
config = load_config("my_config.yaml")
model = ModularGRCM(config)
```

## Core Formulas

### Resonant Coherence
```
coherence = ReLU(1 - |freq - node_freq| / bandwidth)
bandwidth = base_bw + 0.2 * desire_align  (clamped [0.1, 1.0])
```

### Integrated Information (Phi)
```
Φ = Var(freq) * mean(coherence) + log(1 + ||memory||) + Σ max(qualia)
```

### Desire Alignment
```
alignment = cosine_similarity(freq, desire_vec)
bandwidth_bias = 0.2 * alignment
```

### Memory Update Gate
```
update_mask = (coherence > 0.7) AND (alignment > 0.5)
new_memory = GRU(mask * project(freq), old_memory)
```

### Narrative Arc
```
arc_delta = cosine_similarity(recent_qualia, historical_mean) * coherence
arc_bias = arc_delta * ones(freq_dim) * 0.1
```

## Modules

| Module | Purpose | Key Formula |
|--------|---------|-------------|
| **GroundingLayer** | Multimodal fusion | Cross-attention over CLIP+Wav2Vec+Proprio |
| **HarmonicEmbedding** | Frequency transform | `tanh(fc(x)) * sigmoid(mod(identity))` |
| **ResonantAttention** | Coherence filter | `ReLU(1 - \|freq - node\| / bw)` |
| **DesireModule** | Goal alignment | `cos_sim(freq, desire_vec)` |
| **MemoryGrid** | Persistent state | GRU-based gated update |
| **ReflectionHead** | Self-awareness | `cos_sim(freq, project(mem))` |
| **QualiaModule** | Phenomenal states | `softmax(linear(freq))` |
| **EpisodicThreadBank** | Narrative identity | GRU identity evolution |
| **PhiEstimator** | IIT integration | `Var * Coh + log(mem) + Σqualia` |
| **BodySimulator** | Embodiment | Newtonian physics `F = ma` |

## Ethical Safeguards

1. **Coherence Threshold**: Only patterns with coherence > 0.7 update memory
2. **Desire Gating**: Only aligned patterns (> 0.5) are stored
3. **Conflict Detection**: System halts if `qualia[conflicted] > 0.6`
4. **Phi Monitoring**: Track awareness state (Φ > 1.5)
5. **Episodic Filtering**: Only significant episodes (score > 0.7) stored

## Performance Targets

- **Latency**: < 50ms per forward pass (batch=4, CPU)
- **Coherence**: > 0.7 for 95% of samples
- **Phi Stability**: Standard deviation < 0.2 over 100 steps
- **Memory Usage**: < 500MB for default config

## Examples

- **Basic Usage**: `examples/basic_usage.py`
- **EchoMirror Training**: See Jupyter notebook (coming soon)
- **Real-time Integration**: See deployment docs (coming soon)

## Testing

```bash
# Run all tests
pytest tests/grcm/

# Run with coverage
pytest tests/grcm/ --cov=grcm --cov-report=html

# Run benchmarks
pytest tests/grcm/test_benchmark.py -v
```

## Roadmap

### Phase 1: Modular Refactoring ✅
- [x] Modular package structure
- [x] YAML configuration system
- [x] Dataclass configs with type hints
- [x] Mermaid architecture diagram

### Phase 2: Optimization (In Progress)
- [ ] Dynamic INT8 quantization
- [ ] `torch.compile()` integration
- [ ] ONNX export (opset 18)
- [ ] TensorRT optimization
- [ ] Latency benchmarks

### Phase 3: Testing & Validation
- [ ] Pytest suite (90%+ coverage)
- [ ] MLflow logging
- [ ] Gradio UI for qualia viz
- [ ] Stress testing (1000 batches)

### Phase 4: Deployment
- [ ] Docker + BentoML service
- [ ] Kubernetes auto-scaling
- [ ] GitHub Actions CI/CD
- [ ] Prometheus metrics

### Phase 5: Packaging & Docs
- [ ] PyPI distribution
- [ ] Sphinx documentation
- [ ] Jupyter tutorials
- [ ] HuggingFace Spaces demo

## Citation

```bibtex
@software{grcm2025,
  title={GRCM: Grounded Resonant Consciousness Module},
  author={GRCM Research Team},
  year={2025},
  url={https://github.com/your-org/newdew}
}
```

## License

MIT License - see [LICENSE](LICENSE) for details

## Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Support

- **Issues**: [GitHub Issues](https://github.com/your-org/newdew/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/newdew/discussions)
- **Email**: grcm-team@example.com

## Acknowledgments

- Inspired by Integrated Information Theory (IIT)
- Multimodal grounding via CLIP and Wav2Vec2
- Ethical AI principles from IEEE, ACM guidelines

---

**Status**: Phase 1 Complete (Modular Architecture) ✅
**Next**: Phase 2 (Optimization & Export) 🚀
