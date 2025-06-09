#!/usr/bin/env python3
"""Test if the ASS caption system is working"""

import sys
sys.path.insert(0, '/Users/davisschwenke/Clippy')

from auto_peak_viral_clipper import AutoPeakViralClipper

print("Testing ASS caption system...")

# Initialize clipper
clipper = AutoPeakViralClipper()
print("✅ Clipper initialized")

# Check if required methods exist
if hasattr(clipper, 'generate_auto_peak_viral_clip'):
    print("✅ generate_auto_peak_viral_clip method exists")
else:
    print("❌ generate_auto_peak_viral_clip method missing")

if hasattr(clipper, 'download_video'):
    print("✅ download_video method exists")
else:
    print("❌ download_video method missing")

# Check dependencies
try:
    import whisper
    print("✅ Whisper is available")
except ImportError:
    print("❌ Whisper is NOT available - this is needed for transcription!")

try:
    import ffmpeg
    print("✅ ffmpeg-python is available")
except ImportError:
    print("❌ ffmpeg-python is NOT available")

print("\nTo test with a video URL, the app needs Whisper installed.")
print("Install with: pip3 install openai-whisper")
