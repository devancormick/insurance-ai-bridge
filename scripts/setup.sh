#!/bin/bash
# setup.sh - Initial project setup

set -e

echo "🚀 Setting up Insurance AI Bridge System..."

# 1. Verify Git configuration
echo "📦 Verifying Git repository..."
if [ ! -d ".git" ]; then
    echo "Initializing Git repository..."
    git init
    git config user.name "devancormick"
    git config user.email "devancormick@users.noreply.github.com"
    git branch -M main
fi

# 2. Check Python version
echo "🐍 Checking Python version..."
python3 --version || echo "Warning: Python 3.11+ required"

# 3. Check Node.js version
echo "📦 Checking Node.js version..."
node --version || echo "Warning: Node.js 18+ required"

# 4. Setup backend
echo "🔧 Setting up backend..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate || source venv/Scripts/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
cd ..

# 5. Setup frontend
echo "⚛️  Setting up frontend..."
cd frontend
npm install
cd ..

# 6. Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your actual credentials"
fi

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your credentials"
echo "2. Run: docker-compose up -d"
echo "3. Open Cursor AI and start development"

