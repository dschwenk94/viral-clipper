#!/usr/bin/env python3
"""
Captions Status Checker
Quick utility to check caption generation status
"""

import os
import json
from datetime import datetime

def check_captions_status():
    """Check status of caption generation system"""
    print("🎬 VIRAL CLIPPER - CAPTIONS STATUS")
    print("=" * 50)
    
    # Check clips directory
    clips_dir = 'clips'
    if os.path.exists(clips_dir):
        video_files = [f for f in os.listdir(clips_dir) if f.endswith('.mp4')]
        caption_files = [f for f in os.listdir(clips_dir) if f.endswith('.ass')]
        
        print(f"📹 Video clips: {len(video_files)}")
        print(f"📝 Caption files: {len(caption_files)}")
        
        # Check for paired files
        paired = 0
        for video in video_files:
            caption_name = video.replace('.mp4', '_captions.ass')
            if caption_name in caption_files:
                paired += 1
        
        print(f"✅ Clips with captions: {paired}/{len(video_files)}")
        
        if video_files:
            print("\n📋 Recent clips:")
            for video in video_files[-3:]:  # Show last 3
                video_path = os.path.join(clips_dir, video)
                size = os.path.getsize(video_path) / (1024*1024)
                mtime = datetime.fromtimestamp(os.path.getmtime(video_path))
                print(f"   {video} ({size:.1f} MB, {mtime.strftime('%Y-%m-%d %H:%M')})")
    else:
        print("📁 Clips directory not found")
    
    # Check dependencies
    print("\n🔧 Dependencies:")
    
    try:
        import whisper
        print("   ✅ Whisper (transcription)")
    except ImportError:
        print("   ❌ Whisper - install with: pip install openai-whisper")
    
    try:
        import cv2
        print("   ✅ OpenCV (face detection)")
    except ImportError:
        print("   ❌ OpenCV - install with: pip install opencv-python")
    
    try:
        import ffmpeg
        print("   ✅ FFmpeg-python")
    except ImportError:
        print("   ❌ FFmpeg-python - install with: pip install ffmpeg-python")
    
    # Check FFmpeg binary
    import subprocess
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ FFmpeg binary")
        else:
            print("   ❌ FFmpeg binary not working")
    except FileNotFoundError:
        print("   ❌ FFmpeg binary not found")
    
    print("\n🎯 Caption system status: READY" if paired > 0 else "\n⚠️  Caption system status: NEEDS SETUP")

if __name__ == "__main__":
    check_captions_status()
