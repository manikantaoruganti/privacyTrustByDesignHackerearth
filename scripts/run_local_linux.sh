#!/bin/bash
set -e

echo "🚀 Starting DocuShield AI (Linux)"

# Check if Python 3.10+ is available
python_cmd="python3"
if ! command -v $python_cmd &> /dev/null; then
    echo "❌ Python 3.10+ is required but not found!"
    exit 1
fi

# Check Python version
python_version=$($python_cmd --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
if [[ $(echo "$python_version 3.10" | awk '{print ($1 >= $2)}') != 1 ]]; then
    echo "❌ Python 3.10+ is required, found $python_version"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "🔧 Creating virtual environment..."
    $python_cmd -m venv .venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source .venv/bin/activate

# Install backend dependencies
echo "📦 Installing backend dependencies..."
pip install -r backend/requirements.txt

# Build frontend if dist doesn't exist
if [ ! -d "frontend/dist" ]; then
    echo "🏗️  Building frontend..."
    ./scripts/build_frontend.sh
fi

# Verify models (optional)
echo "🔍 Verifying models..."
python scripts/verify_models.py || echo "⚠️  Model verification failed (continuing with placeholders)"

# Start the server
echo ""
echo "🌟 Starting DocuShield AI Server..."
echo "🔗 Open http://localhost:8080 in your browser"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

cd backend
python app.py