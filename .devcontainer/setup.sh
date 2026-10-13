#!/bin/bash

# Setup script for GitHub Codespaces

echo "🚀 Setting up Call Center System..."

# Backend setup
cd /workspaces/agentX || cd /workspace/agentX
echo "📦 Installing Python dependencies..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Frontend setup
cd frontend
echo "📦 Installing Node dependencies..."
npm install

echo "✅ Setup complete!"
echo ""
echo "To start the system:"
echo "  1. Terminal 1: cd /workspaces/agentX && source venv/bin/activate && python main.py"
echo "  2. Terminal 2: cd frontend && npm run dev"
echo ""
echo "The UI will be available at the forwarded port (usually https://xxxx-8000.app.github.dev)"

