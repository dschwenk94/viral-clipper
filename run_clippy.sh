#!/bin/bash
# Clippy Launch Script

echo "🎯 Starting Clippy Multi-User Server..."
echo "📝 Using ASS Caption System V6 (Speech Sync)"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Check if dependencies are installed
pip show flask > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "📥 Installing dependencies..."
    pip install -r requirements_webapp.txt
fi

# Check environment variables
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "Creating from template..."
    cp .env.example .env
    echo "Please edit .env with your configuration"
    exit 1
fi

# Run the application
echo "🚀 Launching Clippy on http://localhost:5000"
python app.py
