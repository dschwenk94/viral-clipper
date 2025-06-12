#!/bin/bash
# Runner script for Clippy app

echo "🎯 Starting Clippy with system Python..."
echo "Note: Make sure you have installed dependencies with: pip3 install -r requirements_webapp.txt"
echo ""

# Try to find the correct Python with Flask installed
if command -v /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 &> /dev/null; then
    echo "Using Python 3.13..."
    /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 app.py
elif command -v /usr/local/bin/python3 &> /dev/null; then
    echo "Using /usr/local/bin/python3..."
    /usr/local/bin/python3 app.py
elif command -v python3 &> /dev/null; then
    echo "Using default python3..."
    python3 app.py
else
    echo "❌ Python 3 not found!"
    echo "Please install Python 3 and the required dependencies."
fi
