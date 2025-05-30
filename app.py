#!/usr/bin/env python3
"""
🎯 VIRAL CLIPPER WEB APP 🎯 - FIXED VERSION WITH OAUTH
Flask web application for the viral clip generator with:
1. Refresh button maintaining state
2. Pop-out effect color consistency
3. Full YouTube OAuth integration and upload
"""

from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect, url_for
from flask_socketio import SocketIO, emit
import os
import json
import uuid
import threading
import time
import pickle
from datetime import datetime
from auto_peak_viral_clipper import AutoPeakViralClipper

# OAuth imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

app = Flask(__name__)
app.config['SECRET_KEY'] = 'viral_clipper_secret_key_2025'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize the clipper
clipper = AutoPeakViralClipper()

# Store active jobs
active_jobs = {}

# OAuth configuration
OAUTH_SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
CREDENTIALS_FILE = 'client_secrets.json'
TOKEN_FILE = 'token.pickle'

# Global OAuth service
youtube_upload_service = None
oauth_credentials = None

if __name__ == '__main__':
    # Ensure clips directory exists
    os.makedirs('clips', exist_ok=True)
    
    # Initialize OAuth on startup
    print("🔐 Checking OAuth status...")
    oauth_status = check_oauth_status()
    if oauth_status['authenticated']:
        print(f"✅ OAuth: {oauth_status['message']}")
    else:
        print(f"⚠️  OAuth: {oauth_status['message']}")
        print("   📝 You'll need to authenticate via the web interface to upload videos")
    
    # Run the app
    print("🎯 Starting Viral Clipper Web App with OAuth...")
    print("🌐 Access at: http://localhost:5000")
    print("📤 YouTube upload: " + ("Ready" if oauth_status['authenticated'] else "Requires authentication"))
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
