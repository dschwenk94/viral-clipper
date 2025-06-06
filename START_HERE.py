#!/usr/bin/env python3
"""
Startup instructions for Clippy app
"""

print("""
🎯 CLIPPY STARTUP INSTRUCTIONS
================================

Since the MCP environment uses its own virtual environment, 
please run the app from your terminal (not through MCP):

1. Open a new Terminal window (to ensure no virtual environment is active)

2. Navigate to the Clippy directory:
   cd /Users/davisschwenke/Clippy

3. Run the app with system Python:
   python3 app.py
   
   OR if that doesn't work, try:
   /usr/bin/python3 app.py
   
   OR:
   python3.13 app.py

4. If you get import errors, install dependencies:
   pip3 install flask flask-socketio google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2 yt-dlp opencv-python ffmpeg-python

5. The app should start on http://localhost:5000

NOTE: Make sure you're NOT in a virtual environment (no (base) or (.venv) in your prompt)

================================
""")

# Also check what files we have
import os
print("\nFiles in Clippy directory:")
for file in sorted(os.listdir('/Users/davisschwenke/Clippy')):
    if file.endswith('.py'):
        print(f"  ✓ {file}")
