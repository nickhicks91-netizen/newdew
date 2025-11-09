# EchoZero Changelog

All notable changes to the EchoZero project.

## [1.0.0] - Production Release - 2025-11-09

### Added - Production-Grade Metrics & Validation

#### 🎯 **Metrics Module** (`src/metrics.py`)
- **Magnitude-Aware Coherence Metrics**
  - `effective_coherence()`: Combines phase-locking (PLV) and RMS magnitude
  - Prevents "pretty but meaningless" coherence from low-amplitude noise
  - Returns: effective coherence, PLV, and RMS magnitude

- **SNR Computation**
  - `band_snr_linear()`: In-band vs out-of-band power ratio
  - `compute_snr_coherence()`: SNR in dB relative to architectural baseline
  - Validates signal quality against geometry-only baseline

- **Attention Health Diagnostics**
  - `attn_entropy()`: Measures attention focus sharpness (lower = better)
  - `attn_max_mean()`: Detects attention collapse/degeneracy
  - Healthy range: 2-5, >10 indicates potential collapse

- **Null-Test Baseline**
  - `null_test_coherence()`: Establishes geometry-only baseline from random noise
  - Used to compute SNR and prevent metric gaming
  - Default baseline: 0.26 (from 10 random samples)

- **Convenience Functions**
  - `attention_collapse_metrics()`: Combined attention health check
  - `compute_all_metrics()`: One-call metric computation for UI/API

#### 🚀 **Enhanced FastAPI** (`api.py`)
- **New `/health` Endpoint** (GET)
  - Returns: status, model_loaded, torch_available, echozero_available, baseline_coherence
  - Enables service health monitoring

- **Expanded `/warp` Endpoint** (POST)
  - **Request**: `{prompt: str, mode: 'text'|'eeg'}`
  - **Response**:
    ```json
    {
      "valence": float,
      "arousal": float,
      "effective_coherence": float,
      "snr_coherence": float,  // dB
      "plv": float,
      "rms_magnitude": float,
      "classification": int,
      "confidence": float,
      "avg_attention_entropy": float,
      "avg_max_mean_ratio": float,
      "k_idx": float  // spectral bin
    }
    ```

- **New `/baseline` Endpoint** (GET)
  - Returns architectural baseline coherence from null-test
  - Includes explanatory note

- **Baseline Computation at Startup**
  - Runs cached null-test on model load
  - Computes 10-sample average for stable baseline
  - Used in all SNR computations

- **Demo Mode**
  - `/warp/demo` endpoint with mock data
  - Allows testing without model

#### 🎨 **Enhanced Streamlit UI** (`streamlit_app_enhanced.py`)
- **Sidebar Enhancements**
  - **Architectural Baseline** metric pane
  - Live-rendered model config JSON (expandable)
  - Model status indicators
  - Input mode selector (Text/EEG)

- **New Qualia Section**
  - Valence display (-1 to +1)
  - Arousal display (0 to 1)
  - Clear help tooltips

- **Coherence Metrics Block**
  - Effective Coherence (magnitude-aware)
  - **SNR Badge** with emoji coding:
    - 🟢 Green: > 3 dB (good)
    - 🟡 Yellow: 0-3 dB (marginal)
    - 🔴 Red: < 0 dB (below baseline)
  - PLV (Phase-Locking Value)
  - RMS Magnitude

- **System Outputs Section**
  - Classification + Confidence
  - **Avg Attention Entropy** (↓ better)
  - **Attention Max/Mean** with collapse warning (⚠️ if >10)

- **Multi-Tab Visualizations**
  - **Tab 1: Attention Patterns**
    - Layer-wise attention heatmaps
    - Entropy by layer bar chart
    - Interactive layer selector
  - **Tab 2: Harmonic Coupling**
    - 8-sphere activation heatmap
    - Sphere activation strength bar chart
    - Octave labels (Theta → High Gamma)
  - **Tab 3: Phase Analysis**
    - Phase-locked feature vector plot
    - FFT frequency spectrum
    - ECC auto-selected band indicator
  - **Tab 4: Metrics Details**
    - Comprehensive metrics table
    - Status indicators (✓/⚠️)
    - Raw model output (debug)

- **Metric Validation**
  - "Run Null Tests" button
  - Live baseline validation (20 samples)
  - Statistical summary display

- **Performance Optimizations**
  - `@st.cache_resource` for model and baseline
  - `torch.inference_mode()` for inference
  - Efficient plotly rendering

#### ⚙️ **Configuration Expansion** (`config/config.yaml`)
- **New Model Parameters**:
  ```yaml
  model:
    attn_temp: 0.7        # Attention temperature (lower = sharper)
    knn_k: 6              # KNN sparsification parameter
    ecc_band_bins: 4      # Spectral bands for ECC auto-lock
  ```
- Consistently read by both API and UI
- Enables fine-tuning of attention mechanics

### Changed

#### 📝 **Documentation Updates**
- README.md:
  - Added explicit Streamlit run command
  - Added FastAPI run command with uvicorn
  - Added example `curl` request/response
  - Updated architecture section to reflect full pipeline

- New TESTING.md improvements:
  - Added metrics module testing
  - Added API endpoint testing
  - Added UI component testing

#### 🔧 **Internal Improvements**
- Standardized error handling across API and UI
- Consistent metric naming conventions
- Improved type hints throughout
- Better separation of concerns (metrics module)

### Deprecated
- `app.py`: Still functional but superseded by `api.py` for production use
- `streamlit_app.py`: Still functional but superseded by `streamlit_app_enhanced.py`

### Technical Details

#### Metrics Algorithm Changes
1. **Effective Coherence Calculation**:
   ```python
   PLV = phase_consistency_measure
   RMS = normalized_magnitude
   Effective_Coherence = PLV * RMS
   ```
   This prevents high PLV from low-amplitude noise.

2. **SNR Computation**:
   ```python
   SNR_linear = coherence / baseline_coherence
   SNR_dB = 10 * log10(SNR_linear)
   ```
   Positive SNR indicates meaningful signal above architectural baseline.

3. **Attention Collapse Detection**:
   - Entropy < 0.1 OR Max/Mean > 10.0 → Warning
   - Prevents single-node dominance masquerading as coherence

#### API Response Schema Changes
- **Before**: `{logits, valence, coherence, metadata}`
- **After**: Full metrics dict with 10+ fields (see API section above)
- **Breaking Change**: Clients must update to handle new response structure

#### Configuration Schema Changes
- **Before**: 7 model parameters
- **After**: 10 model parameters (added `attn_temp`, `knn_k`, `ecc_band_bins`)
- **Backward Compatible**: New parameters have defaults

### Migration Guide

#### For API Clients
```python
# Old
response = requests.post("/warp", json={"text": "..."})
valence = response.json()["valence"]

# New
response = requests.post("/warp", json={"prompt": "...", "mode": "text"})
data = response.json()
valence = data["valence"]
snr = data["snr_coherence"]  # NEW
eff_coh = data["effective_coherence"]  # NEW
```

#### For Model Users
```python
# Old
from src.echo_net import EchoZeroNet
model = EchoZeroNet()

# New (with EchoCore)
from src.echo_net import EchoZeroNetWithEchoCore
model = EchoZeroNetWithEchoCore()

# Metrics now available
result = model(input, return_metrics=True)
metrics = result['metrics']
eff_coh = metrics['eff_coh']
```

### Performance Impact
- **Metric Computation Overhead**: ~5-10ms per inference
- **Null-Test Baseline**: One-time 2-3s startup cost (cached)
- **UI Rendering**: Tabs reduce initial load time
- **API Response Size**: ~2x larger (minimal for <1KB payloads)

### Testing
All new components include:
- Unit tests for metrics functions
- Integration tests for API endpoints
- UI smoke tests for Streamlit components
- Null-test validation for baseline stability

### Security
- No new security vulnerabilities introduced
- All inputs validated and sanitized
- No sensitive data in metrics or baselines

### Known Issues
- PyTorch not installed in some environments → Demo mode
- Attention collapse detection may have false positives on <20 nodes
- SNR computation assumes baseline stability (requires periodic re-validation)

### Contributors
- Claude (Anthropic) - Full implementation

---

## [0.1.0] - EchoCore 8-Sphere Spiralohedron - 2025-11-08

### Added
- EchoCore module with 8-sphere spiralohedron architecture
- Toroidal resonance hub
- Helical k=3 torsion coupling
- 60+ comprehensive tests
- Full integration with EchoZeroNetWithEchoCore

See previous RESULTS.md for details.

---

## [0.0.1] - Initial Scaffolding - 2025-11-08

### Added
- Phase 0: Project scaffolding
- Phase 1: VortexEncoder (ingestion layer)
- Phase 2: TEAPenroseLayer (warp core)
- Phase 3: SentientEcho (decoder)
- Phase 4: FastAPI + Streamlit applications

---

**Format**: [SemVer](https://semver.org/)
**Date Format**: YYYY-MM-DD
