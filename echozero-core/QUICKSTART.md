# EchoZero Quick Start Guide

## 🚀 Get Started in 5 Minutes

This guide shows you how to use the production-grade EchoZero system with magnitude-aware metrics.

---

## Step 1: Install Dependencies

```bash
cd echozero-core

# Install all required packages
pip install -r requirements.txt

# Verify PyTorch installation
python -c "import torch; print(f'PyTorch {torch.__version__} installed ✓')"
```

**Expected output:** `PyTorch 2.x.x installed ✓`

---

## Step 2: Choose Your Interface

You have **3 ways** to use EchoZero:

### Option A: Interactive Web UI (Recommended for Exploration) 🎨

```bash
cd echozero-core
streamlit run streamlit_app_enhanced.py
```

**What you'll see:**
- Opens browser at `http://localhost:8501`
- Sidebar shows architectural baseline coherence
- Input your text prompt
- Get real-time metrics with SNR badges (🟢🟡🔴)
- 4 visualization tabs:
  - **Attention Patterns** - See which nodes focus where
  - **Harmonic Coupling** - 8-sphere resonance heatmap
  - **Phase Analysis** - FFT spectrum and phase vectors
  - **Metrics Details** - Complete diagnostic data

**Try it:**
1. Enter: *"I feel energized and focused"*
2. Click "Warp Through EchoZero"
3. Check the SNR badge:
   - 🟢 **> 3 dB** = Good signal quality
   - 🟡 **0-3 dB** = Marginal
   - 🔴 **< 0 dB** = Below baseline
4. Explore the 4 tabs to see attention, harmonics, and phase analysis

---

### Option B: REST API (For Integration) 🔌

**Start the API server:**
```bash
cd echozero-core
uvicorn api:app --host 0.0.0.0 --port 8000
```

**Test the endpoints:**

**1. Health Check:**
```bash
curl http://localhost:8000/health
```
Response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "torch_available": true,
  "echozero_available": true,
  "baseline_coherence": 0.2634
}
```

**2. Get Baseline:**
```bash
curl http://localhost:8000/baseline
```
Response:
```json
{
  "baseline_coherence": 0.2634,
  "baseline_std": 0.0123,
  "baseline_plv": 0.2812,
  "baseline_rms": 0.4521
}
```

**3. Process Text (Main Endpoint):**
```bash
curl -X POST http://localhost:8000/warp \
  -H "Content-Type: application/json" \
  -d '{"text": "I feel energized and focused"}'
```

Response:
```json
{
  "valence": 0.72,
  "arousal": 0.68,
  "effective_coherence": 0.4123,
  "snr_coherence": 4.23,
  "plv": 0.5234,
  "rms_magnitude": 0.7891,
  "classification": 2,
  "confidence": 0.89,
  "avg_attention_entropy": 0.87,
  "avg_max_mean_ratio": 3.42,
  "k_idx": 2.0
}
```

**Metric Interpretation:**
- `effective_coherence`: Combined PLV × RMS (0-1, higher = more coherent)
- `snr_coherence`: Signal quality in dB (>3 = good, 0-3 = marginal, <0 = poor)
- `plv`: Phase-locking value (0-1, phase consistency)
- `rms_magnitude`: Signal amplitude (higher = stronger)
- `avg_attention_entropy`: Focus sharpness (lower = sharper, healthy < 1.0)
- `avg_max_mean_ratio`: Collapse detector (2-5 = healthy, >10 = collapse)

---

### Option C: Python API (For Scripts) 🐍

**Create a test script:**
```python
# test_echozero.py
import torch
from src.echo_net import create_echozero_model_with_echo_core
from src.metrics import compute_all_metrics, null_test_coherence

# Load model
config_path = "config/config.yaml"
model = create_echozero_model_with_echo_core(config_path)
model.eval()

# Compute baseline
print("Computing architectural baseline...")
baseline_results = null_test_coherence(model, num_samples=10, device='cpu')
baseline = baseline_results['baseline_avg']
print(f"Baseline coherence: {baseline:.4f}")

# Process input
text = "I feel energized and focused"
with torch.inference_mode():
    outputs = model(text)

# Get comprehensive metrics
metrics = compute_all_metrics(
    model=model,
    phase_locked=outputs['phase_locked'],
    amp_locked=outputs['amp_locked'],
    attention=outputs['attention'],
    k_idx=outputs['k_idx'],
    baseline_coherence=baseline
)

# Display results
print(f"\nMetrics for: '{text}'")
print(f"  Effective Coherence: {metrics['effective_coherence']:.4f}")
print(f"  SNR (dB): {metrics['snr_coherence']:.2f}")
print(f"  PLV: {metrics['plv']:.4f}")
print(f"  RMS Magnitude: {metrics['rms_magnitude']:.4f}")
print(f"  Attention Entropy: {metrics['avg_attention_entropy']:.4f}")
print(f"  Max/Mean Ratio: {metrics['avg_max_mean_ratio']:.2f}")

# Interpret SNR
if metrics['snr_coherence'] > 3.0:
    print("  Quality: 🟢 Good signal")
elif metrics['snr_coherence'] > 0:
    print("  Quality: 🟡 Marginal signal")
else:
    print("  Quality: 🔴 Below baseline")
```

**Run it:**
```bash
cd echozero-core
python test_echozero.py
```

---

## Step 3: Understanding the Metrics

### 🎯 Key Metrics Explained

**1. Effective Coherence** (Magnitude-Aware)
- Combines phase consistency (PLV) with signal amplitude (RMS)
- Formula: `PLV × normalized_RMS`
- **Why?** Prevents low-amplitude noise from appearing coherent
- Range: 0-1 (higher = better)

**2. SNR (Signal-to-Noise Ratio)**
- Compares your signal to architectural baseline
- Formula: `10 × log10(coherence / baseline)`
- **Interpretation:**
  - 🟢 **> 3 dB**: Good coherent signal
  - 🟡 **0-3 dB**: Marginal, barely above noise
  - 🔴 **< 0 dB**: Below baseline, mostly noise
- **Typical baseline**: ~0.26 (from random noise)

**3. Attention Health**
- **Entropy** (lower = sharper focus)
  - Healthy: < 1.0
  - Diffuse: > 2.0
- **Max/Mean Ratio** (collapse detector)
  - Healthy: 2-5
  - Collapse: > 10 (single node dominance)

**4. Phase-Locking Value (PLV)**
- Measures phase consistency across network
- Range: 0-1
- Does NOT account for magnitude (see Effective Coherence)

**5. RMS Magnitude**
- Signal amplitude strength
- Higher = stronger activation

---

## Step 4: Validation Tests

Run the verification checklist to ensure everything works:

```bash
cd echozero-core

# Test 1: Import metrics module
python -c "from src.metrics import effective_coherence, null_test_coherence; print('✓ Metrics imported')"

# Test 2: Run metrics smoke test
python src/metrics.py

# Test 3: Test API
uvicorn api:app --port 8000 &
sleep 5
curl http://localhost:8000/health
curl http://localhost:8000/baseline
pkill -f "uvicorn api:app"

# Test 4: Full verification (34-point checklist)
# Follow steps in VERIFICATION.md
```

---

## Step 5: Example Workflows

### Workflow 1: Analyze Emotional Text

**Using Streamlit UI:**
1. `streamlit run streamlit_app_enhanced.py`
2. Enter: *"I'm anxious about the presentation tomorrow"*
3. Click "Warp Through EchoZero"
4. Check metrics:
   - **Valence**: Should be negative (anxiety)
   - **Arousal**: Should be high (anxious energy)
   - **SNR**: Indicates signal quality
5. Navigate to **Attention Patterns** tab
6. See which layers focus on "anxious" vs "presentation"

### Workflow 2: Batch Processing via API

```bash
# Start API
uvicorn api:app --port 8000 &

# Process multiple texts
texts=("I'm happy" "I'm sad" "I'm neutral" "I'm excited")

for text in "${texts[@]}"; do
  echo "Processing: $text"
  curl -X POST http://localhost:8000/warp \
    -H "Content-Type: application/json" \
    -d "{\"text\": \"$text\"}" | jq '.effective_coherence, .snr_coherence'
done
```

### Workflow 3: Null-Test Validation

Validate that your baseline is correctly computed:

**In Streamlit UI:**
1. Click "Run Null Tests" button (bottom of sidebar)
2. Wait 10-20 seconds (computes 10+ samples)
3. Compare to displayed baseline
4. Should be consistent (within 5%)

**Via Python:**
```python
from src.echo_net import create_echozero_model_with_echo_core
from src.metrics import null_test_coherence

model = create_echozero_model_with_echo_core("config/config.yaml")
results = null_test_coherence(model, num_samples=20, device='cpu')

print(f"Baseline: {results['baseline_avg']:.4f} ± {results['baseline_std']:.4f}")
print(f"Expected: ~0.26 (typical for this architecture)")
```

---

## Configuration Tuning

Edit `config/config.yaml` to adjust behavior:

```yaml
model:
  num_nodes: 20          # Graph size
  dim: 128               # Embedding dimension
  num_layers: 5          # Depth

  # NEW: Production parameters
  attn_temp: 0.7         # Attention temperature
                         # Lower = sharper focus
                         # Range: 0.3-1.5

  knn_k: 6               # KNN sparsification
                         # Higher = more connections
                         # Range: 4-8

  ecc_band_bins: 4       # Spectral bands for ECC
                         # More bins = finer frequency control
                         # Range: 2-8 (must divide dim)
```

**Restart required after config changes!**

---

## Troubleshooting

**Problem: "ModuleNotFoundError: No module named 'torch'"**
```bash
pip install torch>=2.1.0
```

**Problem: "Config file not found"**
```bash
cd echozero-core  # Ensure you're in the right directory
ls config/config.yaml  # Should exist
```

**Problem: "Baseline coherence is NaN or 0"**
- Check PyTorch installation: `python -c "import torch; print(torch.__version__)"`
- Verify config: `cat config/config.yaml`
- Run smoke test: `python src/metrics.py`

**Problem: Streamlit shows "Connection error"**
```bash
# Kill any existing Streamlit processes
pkill -f streamlit
# Restart
streamlit run streamlit_app_enhanced.py
```

**Problem: API returns 500 errors**
- Check logs: `uvicorn api:app --log-level debug`
- Verify model loads: `python -c "from src.echo_net import create_echozero_model_with_echo_core; create_echozero_model_with_echo_core('config/config.yaml')"`

---

## Next Steps

✅ **You're ready!** The system is fully functional.

**Recommended path:**
1. Start with **Streamlit UI** to explore interactively
2. Read **CHANGELOG.md** for detailed feature documentation
3. Follow **VERIFICATION.md** for production deployment
4. Integrate with your application via **REST API**

**Advanced topics:**
- Training: See `train.py` and `TESTING.md`
- Custom metrics: Extend `src/metrics.py`
- Docker deployment: `docker-compose up`
- Standalone app: See `STANDALONE.md`

---

## Quick Reference

| Task | Command |
|------|---------|
| Interactive UI | `streamlit run streamlit_app_enhanced.py` |
| REST API server | `uvicorn api:app --port 8000` |
| Health check | `curl http://localhost:8000/health` |
| Process text | `curl -X POST http://localhost:8000/warp -H "Content-Type: application/json" -d '{"text": "..."}'` |
| Run tests | `python src/metrics.py` |
| Verification | Follow `VERIFICATION.md` |

---

**Questions?** See `CHANGELOG.md` for detailed documentation or `VERIFICATION.md` for troubleshooting.
