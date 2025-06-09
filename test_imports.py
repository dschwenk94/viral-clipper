#!/usr/bin/env python3
"""Test if all required modules can be imported"""

print("Testing imports...")

try:
    print("1. Importing srt_viral_caption_system...")
    from srt_viral_caption_system import SRTViralCaptionSystem
    print("   ✅ Success")
except Exception as e:
    print(f"   ❌ Failed: {e}")

try:
    print("2. Importing auto_peak_viral_clipper_srt...")
    from auto_peak_viral_clipper_srt import AutoPeakViralClipperSRT
    print("   ✅ Success")
except Exception as e:
    print(f"   ❌ Failed: {e}")

try:
    print("3. Testing app.py imports...")
    from flask import Flask
    from flask_socketio import SocketIO
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    print("   ✅ All Flask/OAuth imports successful")
except Exception as e:
    print(f"   ❌ Flask/OAuth import failed: {e}")

print("\nTest complete!")
