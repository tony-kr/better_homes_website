#!/bin/bash

echo "🏛️  Architecture Portfolio - Installation Script"
echo "=================================================="
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null
then
    echo "❌ Node.js is not installed!"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

echo "✓ Node.js found: $(node --version)"
echo "✓ npm found: $(npm --version)"
echo ""

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ package.json not found!"
    echo "Please run this script from the architecture-portfolio directory"
    exit 1
fi

echo "📦 Installing dependencies..."
echo ""

npm install

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Installation complete!"
    echo ""
    echo "🚀 Quick Start Commands:"
    echo "------------------------"
    echo "Start development server:  npm run dev"
    echo "Build for production:      npm run build"
    echo "Preview production build:  npm run preview"
    echo ""
    echo "📚 Documentation:"
    echo "----------------"
    echo "README.md              - Project overview and features"
    echo "IMPLEMENTATION_GUIDE.md - Step-by-step customization"
    echo "DESIGN_CONCEPTS.md     - Alternative design ideas"
    echo ""
    echo "🎨 To start developing:"
    echo "   npm run dev"
    echo ""
    echo "Then open http://localhost:5173 in your browser"
    echo ""
else
    echo ""
    echo "❌ Installation failed!"
    echo "Please check the error messages above and try again."
    exit 1
fi
