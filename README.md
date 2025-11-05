# Interactive 3D Heart Simulator - Biohybrid Digital Twin

A fully functional biohybrid heart simulator with real-time 3D visualization, telemetry, and hardware export capabilities.

## 🚀 Quick Start

### Option 1: Download and Open (Easiest)

1. **Download** `heart_simulator_standalone.html` to your computer
2. **Double-click** the file to open it in your default browser
3. **That's it!** The simulator will start automatically

### Option 2: Copy File Path

If double-clicking doesn't work:

1. Right-click `heart_simulator_standalone.html`
2. Select "Copy Path" or "Copy as Path"
3. Paste the path into your browser's address bar
4. Press Enter

### Option 3: Browser File Menu

1. Open your web browser (Chrome, Firefox, Edge, Safari)
2. Press `Ctrl+O` (or `Cmd+O` on Mac)
3. Navigate to `/home/user/newdew/heart_simulator_standalone.html`
4. Click "Open"

## 📋 Requirements

- **Modern web browser** (Chrome, Firefox, Edge, Safari)
- **Internet connection** (only for first load to download libraries)
- **WebGL support** (enabled by default in all modern browsers)

## 🎮 How to Use

### Interactive 3D View
- **Click and drag** to rotate the heart
- **Scroll** to zoom in/out
- **Right-click and drag** to pan

### Controls

#### Basic Parameters
- **Heart Rate Slider**: Adjust from 40-120 BPM
- **SVR Slider**: Set Systemic Vascular Resistance (800-1600)

#### Advanced Features
- **Baroreflex Toggle**: Enable autonomous blood pressure regulation
- **BiVACOR Validation**: Compare simulation against real device benchmarks
- **Phantom Flow Mode**: Enable flow field computation for hardware
- **Export Button**: Download CSV data for actuator control
- **Colorize Chambers**: View anatomical chamber colors
  - Blue = Right Atrium (RA)
  - Purple = Left Atrium (LA)
  - Green = Right Ventricle (RV)
  - Yellow = Left Ventricle (LV)

#### Playback Controls
- **Pause/Play**: Stop or resume the simulation
- **Reset**: Restart with current parameters

## 📊 Features

### Core Simulation
- **4-Chamber Heart Model**: 48 nodes (12 per chamber)
- **FitzHugh-Nagumo Dynamics**: Realistic electrical coupling
- **SA Node Pacemaker**: Simulated at Right Atrium
- **Real-time Physics**: 5ms timestep integration

### Telemetry Dashboard
- **Live Metrics**: Heart rate, cardiac output, blood pressure
- **ECG Waveform**: Real-time electrical activity
- **Coherence Monitor**: Chamber synchronization indicator
- **Historical Charts**: 200-sample rolling window

### Hardware Integration
- **CSV Export**: Download telemetry for actuators
- **PWM Signals**: SA node activation (0-255)
- **Flow Field Data**: Per-chamber flow rates
- **Timestamp Syncing**: Millisecond-precision timing

### Validation
- **BiVACOR Benchmark**: Compare against clinical device
- **8 Heart Rate Points**: 50-120 BPM reference data
- **Real-time Error**: Percentage deviation display
- **Color-coded Feedback**: Green (<10%), Yellow (<20%), Red (>20%)

## 🔧 Technical Details

### Architecture
- **Single HTML File**: 29KB, fully portable
- **No Server Required**: Runs entirely in browser
- **CDN Libraries**:
  - Three.js v0.128.0 (3D rendering)
  - Chart.js v3.7.1 (telemetry graphs)
  - Tailwind CSS (styling)

### Physics Model
```
FitzHugh-Nagumo Equations:
dv/dt = (v - v³/3 - w + I₀ + I_coupling) × 15
dw/dt = (v + 0.7 - 0.8w) × 0.12

Baroreflex Control:
I₀(SA) = base_I₀ - (MAP_error × 0.002 × sensitivity)
```

### Performance
- **60 FPS rendering** with smooth animations
- **200 data points** in telemetry charts
- **500 samples** in export buffer
- **Real-time computation** of 48-node network

## 📦 File Structure

```
/home/user/newdew/
├── heart_simulator_standalone.html  ← USE THIS FILE (complete with docs)
├── index.html                       ← Original version
└── README.md                        ← This file
```

## 🐛 Troubleshooting

### Browser Shows Blank Page
- **Check internet**: Libraries load from CDNs
- **Enable JavaScript**: Required for simulation
- **Update browser**: Use latest version
- **Check console**: Press F12 to see errors

### 3D View Not Showing
- **Enable WebGL**: Check browser settings
- **Update drivers**: Ensure graphics drivers are current
- **Try another browser**: Chrome usually works best

### Slow Performance
- **Close other tabs**: Free up memory
- **Reduce window size**: Smaller viewport = faster rendering
- **Disable other features**: Turn off validation/phantom mode

### Export Not Working
- **Run simulation first**: Need data to export
- **Check downloads folder**: File saves automatically
- **Popup blocker**: May prevent download, allow popups

## 📝 Export Data Format

### CSV Structure
```csv
timestamp,hr_bpm,co_lpm,sys_mmhg,dias_mmhg,coherence,hr_ms,pwm_sa
1730804400000,70.25,5.123,112.5,84.4,0.876,857.1,142
...
```

### Phantom Flow Field (when enabled)
```csv
# Phantom Flow Field Data
# Timestamp: 1730804400000
# RA: 0.6234
# LA: 0.5891
# RV: 0.7102
# LV: 0.8456
```

## 🏥 Clinical Relevance

This simulator is designed for:
- **Medical device research** (TRL 5)
- **Hardware prototyping** (actuator control)
- **Clinical training** (physiology education)
- **Algorithm validation** (benchmark testing)

**Note**: This is a research tool, not for clinical diagnosis or treatment.

## 📄 License & Credits

**Technology Readiness Level**: 5 (Component validation in relevant environment)

**Physics Model**: FitzHugh-Nagumo coupled oscillators
**Validation Data**: BiVACOR TAH benchmark
**3D Rendering**: Three.js
**Telemetry**: Chart.js

## 🆘 Support

If you encounter issues:
1. Check this README
2. Inspect browser console (F12)
3. Try a different browser
4. Verify internet connection (for CDN libraries)

## 🎯 Version

**Phase**: 2 - Biohybrid Control
**Date**: 2025-11-05
**File**: heart_simulator_standalone.html
**Size**: 29KB

---

**Enjoy exploring cardiac dynamics! 🫀**
