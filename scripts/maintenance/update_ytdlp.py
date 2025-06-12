#!/usr/bin/env python3
"""
Update yt-dlp to fix YouTube download issues
"""

import subprocess
import sys

def update_ytdlp():
    """Update yt-dlp to the latest version"""
    print("Updating yt-dlp to fix YouTube download issues...")
    
    try:
        # Update yt-dlp
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ yt-dlp updated successfully!")
            print(result.stdout)
            
            # Check version
            import yt_dlp
            print(f"\nyt-dlp version: {yt_dlp.version.__version__}")
            
        else:
            print(f"❌ Failed to update yt-dlp: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    update_ytdlp()
