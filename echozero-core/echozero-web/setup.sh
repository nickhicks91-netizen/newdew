#!/bin/bash
# EchoZero Web Setup Script

echo "🌀 EchoZero Web - Setup Script"
echo "================================"
echo ""

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js ≥ 18"
    echo "   Download from: https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "⚠️  Node.js version $NODE_VERSION detected. Recommended: ≥ 18"
fi

echo "✓ Node.js $(node -v) detected"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ npm install failed"
    exit 1
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Quick Start:"
echo ""
echo "  1. Start the backend API:"
echo "     cd .. && uvicorn api:app --port 8000"
echo ""
echo "  2. In a new terminal, start the web app:"
echo "     npm run dev"
echo ""
echo "  3. Open http://localhost:3000"
echo ""
echo "📖 For more info, see README.md"
echo ""
