#!/bin/bash

echo "🚀 Setting up PHY64ALL Virtual Environment..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install backend dependencies
echo "🔧 Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
echo "🎨 Installing frontend dependencies..."
cd frontend
pip install -r requirements.txt
cd ..

echo "✅ Setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "  source ~/phy64all/venv/bin/activate"
echo ""
echo "To deactivate when done:"
echo "  deactivate"
