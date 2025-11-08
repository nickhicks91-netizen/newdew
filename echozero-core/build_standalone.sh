#!/bin/bash
# Build EchoZero Standalone Application
#
# This script creates a standalone executable for EchoZero
# that bundles Python, all dependencies, and the application code.
#
# Usage:
#   ./build_standalone.sh

set -e  # Exit on error

echo "=========================================="
echo "  EchoZero Standalone Build Script"
echo "=========================================="
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# Install package in development mode
echo "Installing EchoZero package..."
pip install -e .

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist *.spec __pycache__

# Build standalone executable
echo ""
echo "Building standalone application..."
echo "This may take several minutes..."
echo ""

pyinstaller launcher.spec --clean

# Check if build succeeded
if [ -d "dist/EchoZero" ]; then
    echo ""
    echo "=========================================="
    echo "  ✓ Build successful!"
    echo "=========================================="
    echo ""
    echo "Standalone application created in: dist/EchoZero/"
    echo ""
    echo "To run:"
    echo "  cd dist/EchoZero"
    echo "  ./EchoZero"
    echo ""
    echo "To distribute:"
    echo "  1. Zip the dist/EchoZero folder"
    echo "  2. Share with users"
    echo "  3. Users just extract and run ./EchoZero"
    echo ""
else
    echo "❌ Build failed. Check output above for errors."
    exit 1
fi
