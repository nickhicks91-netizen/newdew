# EchoZero Post-Deploy Verification Checklist

Comprehensive validation checklist for production deployment of EchoZero with magnitude-aware metrics.

## ✅ Pre-Deployment Checks

### 1. Environment Setup
- [ ] Python ≥3.11 installed
- [ ] All dependencies installed: `pip install -r requirements.txt`
- [ ] PyTorch installed and functional: `python -c "import torch; print(torch.__version__)"`
- [ ] Config file exists: `config/config.yaml`
- [ ] All source modules present:
  - [ ] `src/metrics.py`
  - [ ] `src/echo_net.py`
  - [ ] `src/echo_core.py`
  - [ ] `src/ingestion/vortex_encoder.py`
  - [ ] `src/warp/tea_penrose.py`
  - [ ] `src/decode/sentient_echo.py`

### 2. Configuration Validation
- [ ] Config contains all required sections:
  - [ ] `model` (with `attn_temp`, `knn_k`, `ecc_band_bins`)
  - [ ] `encoder`
  - [ ] `decoder`
  - [ ] `echo_core`
  - [ ] `training`
  - [ ] `benchmark`
- [ ] Parameter values are sane:
  - [ ] `attn_temp` > 0 (typically 0.5-1.5)
  - [ ] `knn_k` ≥ 1 (typically 4-8)
  - [ ] `ecc_band_bins` ≥ 2 (typically 4)
  - [ ] `dim` divisible by `ecc_band_bins`

---

## ✅ Metrics Module Verification

### 3. Import Test
```bash
python -c "from src.metrics import effective_coherence, band_snr_linear, attn_entropy, attn_max_mean, null_test_coherence, compute_snr_coherence"
```
- [ ] No import errors
- [ ] All functions available

### 4. Function Tests
```bash
cd echozero-core
python src/metrics.py
```
**Expected Output:**
- [ ] "Testing EchoZero metrics..."
- [ ] Effective Coherence: ~0.5-0.9
- [ ] PLV: ~0.4-0.8
- [ ] RMS: ~0.5-2.0
- [ ] SNR (linear): ~0.5-2.0
- [ ] Entropy: ~0.2-1.5
- [ ] Max/Mean: ~2-5
- [ ] SNR: ~-5 to +10 dB
- [ ] "✓ Metrics module validated!"

### 5. Null-Test Baseline
```python
from src.echo_net import EchoZeroNetWithEchoCore
from src.metrics import null_test_coherence

model = EchoZeroNetWithEchoCore()
baseline = null_test_coherence(model, num_samples=10)
print(f"Baseline: {baseline['baseline_avg']:.4f}")
```
**Validation:**
- [ ] Baseline coherence: 0.20-0.35 (typical range)
- [ ] Baseline std: < 0.10
- [ ] Process completes in <30 seconds

---

## ✅ API Verification

### 6. FastAPI Server Startup
```bash
cd echozero-core
uvicorn api:app --host 127.0.0.1 --port 8000
```
**Check Logs:**
- [ ] "Model loaded: X layers, Y spheres, dim=Z"
- [ ] "Computing architectural baseline..."
- [ ] "Baseline coherence: 0.XXXX"
- [ ] "Application startup complete"
- [ ] No errors or warnings

### 7. Health Endpoint
```bash
curl http://localhost:8000/health
```
**Expected Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "torch_available": true,
  "echozero_available": true,
  "baseline_coherence": 0.26
}
```
**Validation:**
- [ ] `status == "healthy"`
- [ ] `model_loaded == true`
- [ ] `baseline_coherence` in range 0.20-0.35

### 8. Baseline Endpoint
```bash
curl http://localhost:8000/baseline
```
**Expected Response:**
```json
{
  "baseline_coherence": 0.26,
  "note": "Geometry-only coherence from random noise (10 samples)"
}
```
**Validation:**
- [ ] Returns valid baseline value
- [ ] Matches `/health` baseline

### 9. Warp Endpoint (Text Mode)
```bash
curl -X POST http://localhost:8000/warp \
  -H "Content-Type: application/json" \
  -d '{"prompt": "The eight spheres resonate in toroidal harmony", "mode": "text"}'
```
**Expected Response Fields:**
```json
{
  "valence": <float in [-1, 1]>,
  "arousal": <float in [0, 1]>,
  "effective_coherence": <float>,
  "snr_coherence": <float (dB)>,
  "plv": <float>,
  "rms_magnitude": <float>,
  "classification": <int>,
  "confidence": <float>,
  "avg_attention_entropy": <float>,
  "avg_max_mean_ratio": <float>,
  "k_idx": <float>
}
```
**Validation:**
- [ ] All fields present
- [ ] `valence` in range [-1, 1]
- [ ] `arousal` in range [0, 1]
- [ ] `effective_coherence` > 0
- [ ] `snr_coherence` > -10 dB (reasonable)
- [ ] `plv` in range [0, 1]
- [ ] `classification` in [0, num_classes-1]
- [ ] `confidence` in range [0, 1]
- [ ] `avg_attention_entropy` > 0
- [ ] `avg_max_mean_ratio` > 0
- [ ] Response time < 500ms

### 10. Warp Endpoint (EEG Mode)
```bash
curl -X POST http://localhost:8000/warp \
  -H "Content-Type: application/json" \
  -d "{\"prompt\": \"$(python -c 'import random; print(\",\".join([str(random.random()) for _ in range(256)]))')\", \"mode\": \"eeg\"}"
```
**Validation:**
- [ ] Returns valid response
- [ ] No errors on numeric input
- [ ] Metrics within expected ranges

### 11. Demo Endpoint
```bash
curl http://localhost:8000/warp/demo
```
**Validation:**
- [ ] Returns mock data
- [ ] All required fields present

### 12. Error Handling
```bash
# Missing prompt
curl -X POST http://localhost:8000/warp -H "Content-Type: application/json" -d '{"mode": "text"}'
# Invalid mode
curl -X POST http://localhost:8000/warp -H "Content-Type: application/json" -d '{"prompt": "test", "mode": "invalid"}'
```
**Validation:**
- [ ] Returns 422 (validation error)
- [ ] Error message is clear

---

## ✅ UI Verification

### 13. Streamlit Startup
```bash
cd echozero-core
streamlit run streamlit_app_enhanced.py
```
**Check Terminal:**
- [ ] "Model loaded..."
- [ ] "Computing architectural baseline..."
- [ ] No errors
- [ ] "You can now view your Streamlit app in your browser."

### 14. UI Elements (Sidebar)
**Navigate to http://localhost:8501**
- [ ] Page title: "🌀 EchoZero Warp Interface"
- [ ] Sidebar visible
- [ ] "System Configuration" header
- [ ] Model status: "✓ Model Loaded"
- [ ] Metrics display: Layers, Spheres, Dimension
- [ ] "Architectural Baseline" section
- [ ] Baseline value displayed (0.20-0.35)
- [ ] "Model Configuration" expander (contains JSON)
- [ ] "Input Mode" radio: Text/EEG Signal

### 15. Input Section
- [ ] "Input" header visible
- [ ] Text area for prompt (Text mode)
- [ ] Default prompt populated
- [ ] "🌀 Process" button visible
- [ ] Button is primary (blue)

### 16. Processing (Text Mode)
**Steps:**
1. Select "Text" mode
2. Enter prompt: "Test signal for resonance"
3. Click "🌀 Process"

**Validation:**
- [ ] Spinner appears: "Processing through warp core..."
- [ ] Success message: "✓ Processing complete"
- [ ] No errors in console

### 17. Results Display
**After processing, check all sections:**

**Qualia Metrics:**
- [ ] "Qualia Metrics" header
- [ ] Valence metric (with tooltip)
- [ ] Arousal metric (with tooltip)
- [ ] Values in correct ranges

**Coherence Metrics:**
- [ ] "Coherence Metrics (Magnitude-Aware)" header
- [ ] Effective Coherence value
- [ ] SNR with emoji badge (🟢/🟡/🔴)
- [ ] PLV value
- [ ] RMS Magnitude value
- [ ] All tooltips functional

**System Outputs:**
- [ ] "System Outputs" header
- [ ] Classification value
- [ ] Confidence value
- [ ] Avg Attention Entropy value
- [ ] Attention Max/Mean value (with ✓ or ⚠️)
- [ ] Collapse warning if ratio > 10

### 18. Visualization Tabs
**Tab 1: Attention Patterns**
- [ ] Tab exists and clickable
- [ ] Layer slider functional
- [ ] Attention heatmap renders
- [ ] Colorbar present
- [ ] Entropy by layer bar chart renders
- [ ] X-axis labels: L1, L2, ...

**Tab 2: Harmonic Coupling**
- [ ] Tab exists and clickable
- [ ] 8-sphere heatmap renders
- [ ] Y-axis labels: S1-S8 with octave names
- [ ] Sphere activation bar chart renders
- [ ] All 8 spheres visible

**Tab 3: Phase Analysis**
- [ ] Tab exists and clickable
- [ ] Phase-locked feature plot renders
- [ ] FFT spectrum plot renders
- [ ] ECC band indicator displays (k=X)

**Tab 4: Metrics Details**
- [ ] Tab exists and clickable
- [ ] Metrics table renders
- [ ] All 10 metrics present
- [ ] Status column has ✓/⚠️/emoji
- [ ] "Raw Model Output" expander functional
- [ ] JSON displays correctly

### 19. Null Test Validation
**Steps:**
1. Scroll to "Metric Validation" section
2. Click "Run Null Tests (Baseline Validation)"

**Validation:**
- [ ] Spinner appears: "Running null tests..."
- [ ] Success message: "✓ Null test complete"
- [ ] Three metrics display:
  - [ ] Baseline Coherence
  - [ ] Baseline Std
  - [ ] Baseline PLV
- [ ] Info message about baseline usage
- [ ] Values match API baseline

### 20. EEG Mode Processing
**Steps:**
1. Switch to "EEG Signal" mode
2. Enter comma-separated values (256+)
3. Click "🌀 Process"

**Validation:**
- [ ] Processing completes
- [ ] Results display
- [ ] No errors

---

## ✅ Cross-Component Validation

### 21. API ↔ Metrics Consistency
```python
import requests
import torch
from src.echo_net import EchoZeroNetWithEchoCore

# API result
api_response = requests.post("http://localhost:8000/warp", json={"prompt": "test", "mode": "text"}).json()

# Direct model result
model = EchoZeroNetWithEchoCore()
model.eval()
with torch.inference_mode():
    result = model("test", return_metrics=True, return_qualia=True)

# Compare
print(f"API valence: {api_response['valence']}")
print(f"Model valence: {float(result['qualia']['valence'][0])}")
# Should be approximately equal
```
**Validation:**
- [ ] Valence values match (within 0.01)
- [ ] Arousal values match (within 0.01)
- [ ] Effective coherence matches (within 0.01)

### 22. UI ↔ API Consistency
**Steps:**
1. Process same prompt in UI
2. Send same prompt to API via curl
3. Compare results

**Validation:**
- [ ] Valence matches (visual vs API)
- [ ] SNR badge matches (color matches dB range)
- [ ] Attention metrics match

### 23. Baseline Stability
**Run 3 times:**
```python
from src.metrics import null_test_coherence
from src.echo_net import EchoZeroNetWithEchoCore

model = EchoZeroNetWithEchoCore()
baselines = []
for i in range(3):
    result = null_test_coherence(model, num_samples=20)
    baselines.append(result['baseline_avg'])
    print(f"Run {i+1}: {baselines[-1]:.4f}")

import numpy as np
print(f"Mean: {np.mean(baselines):.4f}, Std: {np.std(baselines):.4f}")
```
**Validation:**
- [ ] Mean baseline: 0.20-0.35
- [ ] Std across runs: < 0.05
- [ ] All runs complete successfully

---

## ✅ Performance Validation

### 24. API Latency
```bash
time curl -X POST http://localhost:8000/warp \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test", "mode": "text"}' \
  -o /dev/null -s
```
**Validation:**
- [ ] Response time < 500ms (text mode)
- [ ] Response time < 1000ms (EEG mode)

### 25. UI Responsiveness
- [ ] Page loads in < 3 seconds
- [ ] Inference completes in < 2 seconds
- [ ] Tab switching is instant
- [ ] No lag when interacting with sliders

### 26. Memory Usage
```bash
# During inference
ps aux | grep python | grep -E '(uvicorn|streamlit)'
```
**Validation:**
- [ ] API process < 2GB RAM
- [ ] UI process < 2GB RAM
- [ ] No memory leaks after 10 inferences

---

## ✅ Data Validation

### 27. Metric Range Checks
**Run 100 random inferences:**
```python
import torch
from src.echo_net import EchoZeroNetWithEchoCore

model = EchoZeroNetWithEchoCore()
model.eval()

results = []
for _ in range(100):
    with torch.inference_mode():
        result = model(torch.randn(1024), return_metrics=True)
        results.append(result['metrics'])

# Check ranges
import numpy as np
eff_cohs = [float(r['eff_coh']) for r in results]
plvs = [float(r['plv']) for r in results]
entropies = [float(r['attn_entropy']) for r in results]

print(f"Eff Coh: {np.mean(eff_cohs):.3f} ± {np.std(eff_cohs):.3f}")
print(f"PLV: {np.mean(plvs):.3f} ± {np.std(plvs):.3f}")
print(f"Entropy: {np.mean(entropies):.3f} ± {np.std(entropies):.3f}")
```
**Validation:**
- [ ] Effective coherence: mean 0.3-0.7, std < 0.2
- [ ] PLV: mean 0.4-0.8, std < 0.2
- [ ] Entropy: mean 0.3-1.0, std < 0.3
- [ ] Max/mean: mean 2-8, std < 3
- [ ] No NaN or Inf values

### 28. SNR Validation
**Compare signal vs noise:**
```python
# Real signal (text)
signal_result = model("Meaningful text", return_metrics=True)
signal_coh = float(signal_result['metrics']['eff_coh'])

# Noise
noise_result = model(torch.randn(1024), return_metrics=True)
noise_coh = float(noise_result['metrics']['eff_coh'])

print(f"Signal coherence: {signal_coh:.4f}")
print(f"Noise coherence: {noise_coh:.4f}")
print(f"Ratio: {signal_coh / noise_coh:.2f}")
```
**Validation:**
- [ ] Signal coherence > noise coherence (usually)
- [ ] Ratio > 1.1 (at least 10% better)

---

## ✅ Error Handling

### 29. API Error Cases
```bash
# Invalid JSON
curl -X POST http://localhost:8000/warp -d "invalid"

# Missing fields
curl -X POST http://localhost:8000/warp -H "Content-Type: application/json" -d '{}'

# Invalid mode
curl -X POST http://localhost:8000/warp -H "Content-Type: application/json" -d '{"prompt": "test", "mode": "invalid"}'
```
**Validation:**
- [ ] Returns appropriate HTTP error codes
- [ ] Error messages are clear
- [ ] No server crashes

### 30. UI Error Cases
**Test:**
1. Empty prompt → Click process
2. Invalid EEG data → Click process
3. Switch modes mid-processing

**Validation:**
- [ ] Appropriate error messages shown
- [ ] UI doesn't crash
- [ ] Can recover and process again

---

## ✅ Documentation

### 31. Files Present
- [ ] `CHANGELOG.md` exists and up-to-date
- [ ] `VERIFICATION.md` (this file) exists
- [ ] `README.md` updated with new features
- [ ] `TESTING.md` updated
- [ ] `RESULTS.md` present
- [ ] `STANDALONE.md` present

### 32. README Accuracy
- [ ] Streamlit command correct: `streamlit run streamlit_app_enhanced.py`
- [ ] API command correct: `uvicorn api:app --host 0.0.0.0 --port 8000`
- [ ] curl example works
- [ ] Architecture diagram matches implementation

---

## ✅ Final Sign-Off

### 33. Production Readiness
- [ ] All tests above passed
- [ ] No critical errors in logs
- [ ] Performance acceptable
- [ ] Documentation complete
- [ ] Code committed to repository
- [ ] Branch pushed to remote

### 34. Deployment Notes
**Record:**
- Python version: ___________
- PyTorch version: ___________
- Deployment environment: ___________
- Baseline coherence: ___________
- Date verified: ___________
- Verified by: ___________

---

## 🚨 Common Issues & Solutions

### Issue: "Model not loaded" in API
**Solution:**
```bash
# Check config exists
ls config/config.yaml

# Check imports
python -c "from src.echo_net import EchoZeroNetWithEchoCore"

# Check PyTorch
python -c "import torch; print(torch.__version__)"
```

### Issue: Baseline coherence < 0.15 or > 0.40
**Solution:**
- Re-run null test with more samples (num_samples=50)
- Check model initialization (may be undertrained weights)
- Verify config parameters are reasonable

### Issue: SNR always negative
**Solution:**
- Check baseline value (may be too high)
- Verify effective coherence computation
- Test with known good signal

### Issue: Attention collapse warnings on all inputs
**Solution:**
- Check `attn_temp` parameter (try increasing to 1.0-1.5)
- Verify `knn_k` is not too small
- Check attention matrix normalization

### Issue: UI tabs don't render
**Solution:**
```bash
# Install/update plotly
pip install --upgrade plotly streamlit

# Check imports
python -c "import plotly; import streamlit"
```

---

**Verification Complete!** 🎉

If all checks pass, EchoZero is production-ready with magnitude-aware metrics.
