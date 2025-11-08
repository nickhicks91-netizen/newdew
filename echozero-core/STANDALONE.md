# EchoZero Standalone Application Guide

This guide shows you how to create and distribute EchoZero as a standalone application that users can run without installing Python or dependencies.

## Table of Contents

1. [Quick Start (Desktop Launcher)](#quick-start-desktop-launcher)
2. [Method 1: PyInstaller Executable](#method-1-pyinstaller-executable)
3. [Method 2: Docker Container](#method-2-docker-container)
4. [Method 3: Electron Desktop App](#method-3-electron-desktop-app)
5. [Distribution](#distribution)

---

## Quick Start (Desktop Launcher)

The simplest way to run EchoZero as a standalone app without building an executable:

```bash
# Install dependencies once
pip install -r requirements.txt
pip install -e .

# Run the launcher
python launcher.py
```

This will:
- Start the FastAPI backend (port 8000)
- Start the Streamlit UI (port 8501)
- Open your browser automatically
- Manage both processes together

**Press Ctrl+C to stop everything at once.**

---

## Method 1: PyInstaller Executable

Create a single-file or single-folder executable that bundles everything.

### 1.1 Build on Linux/macOS

```bash
chmod +x build_standalone.sh
./build_standalone.sh
```

### 1.2 Build on Windows

```cmd
build_standalone.bat
```

### 1.3 Manual Build

```bash
# Install PyInstaller
pip install pyinstaller

# Build
pyinstaller launcher.spec --clean

# Output will be in dist/EchoZero/
```

### 1.4 Run the Executable

```bash
# Linux/macOS
cd dist/EchoZero
./EchoZero

# Windows
cd dist\EchoZero
EchoZero.exe
```

### 1.5 Customize Build

Edit `launcher.spec`:

```python
# Change console mode (True = show terminal, False = hidden)
console=False,  # No terminal window

# Add application icon
icon='path/to/icon.ico',  # Windows
icon='path/to/icon.icns',  # macOS

# Create single-file executable (slower startup)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,  # Add these
    a.zipfiles,  # Add these
    a.datas,     # Add these
    [],
    name='EchoZero',
    onefile=True,  # Single file
    # ...
)
```

### 1.6 Troubleshooting PyInstaller

**Issue: "Failed to execute script"**
```bash
# Run with console=True to see errors
# Check launcher.spec and set console=True
```

**Issue: Missing modules**
```bash
# Add to hiddenimports in launcher.spec
hiddenimports=[
    'your_missing_module',
]
```

**Issue: Large executable size**
```bash
# Exclude unnecessary packages
excludes=['matplotlib', 'jupyter'],  # Example
```

---

## Method 2: Docker Container

Run as a containerized application. Best for servers or cloud deployment.

### 2.1 Build and Run with Docker Compose

```bash
# Start both backend and frontend
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

Access at:
- Frontend (UI): http://localhost:8501
- Backend (API): http://localhost:8000

### 2.2 Build Single Container

```bash
# Build
docker build -t echozero:latest .

# Run backend only
docker run -p 8000:8000 echozero:latest \
  uvicorn app:app --host 0.0.0.0 --port 8000

# Run frontend only
docker run -p 8501:8501 echozero:latest \
  streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
```

### 2.3 Deploy to Cloud

**Docker Hub:**
```bash
docker tag echozero:latest yourusername/echozero:latest
docker push yourusername/echozero:latest
```

**AWS ECS / Azure Container Instances / Google Cloud Run:**
```bash
# Use docker-compose.yml as reference
# Configure with cloud provider's container service
```

---

## Method 3: Electron Desktop App

Create a native desktop app with web technologies.

### 3.1 Install Electron

```bash
npm init -y
npm install electron electron-builder
```

### 3.2 Create Electron Main Process

Create `electron-main.js`:

```javascript
const { app, BrowserWindow } = require('electron');
const { spawn } = require('child_process');
const path = require('path');

let mainWindow;
let backendProcess;
let frontendProcess;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  // Start Python processes
  startBackend();
  startFrontend();

  // Wait then load Streamlit
  setTimeout(() => {
    mainWindow.loadURL('http://localhost:8501');
  }, 5000);
}

function startBackend() {
  backendProcess = spawn('python', ['launcher.py'], {
    cwd: path.join(__dirname, 'echozero-core')
  });
}

function startFrontend() {
  // Launcher.py handles this
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (backendProcess) backendProcess.kill();
  if (frontendProcess) frontendProcess.kill();
  app.quit();
});
```

### 3.3 Build Electron App

```bash
# Package for current platform
npx electron-builder

# Package for all platforms
npx electron-builder -mwl
```

---

## Distribution

### Option 1: Distribute PyInstaller Build

**Steps:**
1. Build with PyInstaller: `./build_standalone.sh`
2. Test: `cd dist/EchoZero && ./EchoZero`
3. Compress: `zip -r EchoZero-v1.0-linux.zip dist/EchoZero/`
4. Share the ZIP file

**User Instructions:**
```
1. Extract ZIP file
2. Run EchoZero executable
3. Browser opens automatically to http://localhost:8501
```

### Option 2: Distribute Docker Image

**Steps:**
1. Build: `docker build -t echozero:1.0 .`
2. Save: `docker save echozero:1.0 | gzip > echozero-1.0.tar.gz`
3. Share the TAR file

**User Instructions:**
```bash
# Load image
docker load < echozero-1.0.tar.gz

# Run with docker-compose
docker-compose up -d
```

### Option 3: Installer Package

**Windows (Inno Setup):**
```bash
# Install Inno Setup
# Create installer script (echozero.iss)
# Build: iscc echozero.iss
```

**macOS (DMG):**
```bash
# Use electron-builder or create-dmg
npm install create-dmg
create-dmg dist/EchoZero.app
```

**Linux (AppImage/Snap/Flatpak):**
```bash
# AppImage
pip install appimage-builder
appimage-builder --recipe AppImageBuilder.yml
```

---

## Testing Your Standalone App

### Checklist

- [ ] App starts without errors
- [ ] Backend API is accessible (http://localhost:8000/health)
- [ ] Frontend UI loads (http://localhost:8501)
- [ ] Can create inference requests
- [ ] Attention visualization works
- [ ] Models can be saved/loaded
- [ ] App closes cleanly (Ctrl+C)
- [ ] No Python installation required (for executables)
- [ ] Works on fresh OS install (test in VM)

### Test on Clean System

```bash
# Linux: Use Docker
docker run -it --rm ubuntu:22.04 /bin/bash
# Then test your executable

# Windows: Use Windows Sandbox
# macOS: Use separate user account
```

---

## Performance Optimization

### Reduce Executable Size

1. **Remove unused dependencies:**
   ```python
   # In launcher.spec, add to excludes:
   excludes=['matplotlib', 'jupyter', 'notebook']
   ```

2. **Use UPX compression:**
   ```python
   upx=True,
   upx_exclude=[],
   ```

3. **Lazy import heavy modules:**
   ```python
   # In your code
   def use_heavy_lib():
       import heavy_library  # Import only when needed
   ```

### Faster Startup

1. **Disable unnecessary services:**
   - Remove WandB if not logging
   - Disable MNE auto-downloads
   - Skip model preloading

2. **Use smaller model configs:**
   ```yaml
   # config/config.yaml
   model:
     dim: 64  # Instead of 128
     num_layers: 3  # Instead of 5
   ```

---

## Troubleshooting

### "Port already in use"

```bash
# Check what's using ports
lsof -i :8000  # Linux/macOS
netstat -ano | findstr :8000  # Windows

# Kill the process or change ports in launcher.py
```

### "Module not found"

```bash
# Ensure all dependencies in requirements.txt
# Add missing modules to launcher.spec hiddenimports
```

### "Permission denied"

```bash
# Make executable
chmod +x build_standalone.sh
chmod +x dist/EchoZero/EchoZero
```

### App freezes or crashes

```bash
# Run with console=True to see error messages
# Check logs in ~/.echozero/logs/
```

---

## Advanced: CI/CD for Releases

### GitHub Actions Example

```yaml
# .github/workflows/build-release.yml
name: Build Standalone Releases

on:
  push:
    tags:
      - 'v*'

jobs:
  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: |
          pip install -r requirements.txt pyinstaller
          ./build_standalone.sh
      - uses: actions/upload-artifact@v2
        with:
          name: EchoZero-Linux
          path: dist/EchoZero

  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: |
          pip install -r requirements.txt pyinstaller
          .\build_standalone.bat
      - uses: actions/upload-artifact@v2
        with:
          name: EchoZero-Windows
          path: dist\EchoZero

  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: |
          pip install -r requirements.txt pyinstaller
          ./build_standalone.sh
      - uses: actions/upload-artifact@v2
        with:
          name: EchoZero-macOS
          path: dist/EchoZero
```

---

## Summary

**Easiest:** Use `launcher.py` - requires Python but simple
**Most Portable:** PyInstaller - single executable, no Python needed
**Most Scalable:** Docker - cloud-ready, consistent environment
**Most Native:** Electron - feels like native desktop app

Choose based on your distribution needs and target audience!
