# EchoZero: Resonant AI via Torsion-Warped Lattices

**EchoZero v1.0** is a resonant AI middleware engine based on torsion-warped lattices (TEA architecture). This PyTorch-based modular stack enables geometric deep learning, starting as an LLM filter and scaling to standalone bio-grounded networks.

## Features

- **TEAPenroseLayer**: Ricci-torsion attention on Penrose tilings for coherence funneling
- **VortexEncoder**: Engram compression for multi-modal inputs (text, EEG, spectral)
- **SentientEcho**: Qualia resolution decoder with chiral projections
- **Modular Architecture**: Clean separation of ingestion, warp, and decode layers

## Installation

```bash
pip install -e .
```

## Quick Start

```python
from src.echo_net import EchoZeroNet

# Initialize network
net = EchoZeroNet(num_layers=3, dim=128, mode='text')

# Process input
logits, valence, attention = net("Your prompt here")
```

## Demo

Run the interactive demo:
```bash
jupyter notebook notebooks/demo.ipynb
```

## Development

### Requirements
- Python 3.10+
- PyTorch 2.1.0+
- See `requirements.txt` for full dependencies

### Testing
```bash
pytest --cov=src tests/
```

### Benchmarking
```bash
python train.py --benchmark
```

## Architecture

```
Input → VortexEncoder → TEAPenroseLayer (×N) → SentientEcho → Output
         (FFT + Trefoil)  (Ricci-Torsion Attn)   (Qualia Decode)
```

## Citation

If you use EchoZero in your research, please cite:

```
@software{echozero2025,
  title={EchoZero: Resonant AI via Torsion-Warped Lattices},
  author={Resonant Inventor},
  year={2025}
}
```

## License

MIT License - See LICENSE file for details
