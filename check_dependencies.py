#!/usr/bin/env python3
"""
Dependency Checker for Viral Clipper
Verifies all required dependencies are installed and working
"""

import sys
import subprocess
import importlib

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (Need 3.8+)")
        return False

def check_package(package_name, import_name=None, min_version=None):
    """Check if a package is installed and importable"""
    if import_name is None:
        import_name = package_name
    
    try:
        module = importlib.import_module(import_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"✅ {package_name} ({version})")
        return True
    except ImportError:
        print(f"❌ {package_name} - Not installed")
        return False

def check_ffmpeg():
    """Check FFmpeg installation"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ {version_line}")
            return True
        else:
            print("❌ FFmpeg - Command failed")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg - Not found in PATH")
        return False
    except subprocess.TimeoutExpired:
        print("❌ FFmpeg - Command timeout")
        return False

def main():
    """Main dependency check"""
    print("🎯 VIRAL CLIPPER - DEPENDENCY CHECK")
    print("=" * 50)
    
    all_good = True
    
    # Core requirements
    print("\n🐍 Core Python:")
    all_good &= check_python_version()
    
    # Web framework
    print("\n🌐 Web Framework:")
    all_good &= check_package('Flask', 'flask')
    all_good &= check_package('Flask-SocketIO', 'flask_socketio')
    
    # Video processing
    print("\n🎥 Video Processing:")
    all_good &= check_ffmpeg()
    all_good &= check_package('ffmpeg-python', 'ffmpeg')
    all_good &= check_package('OpenCV', 'cv2')
    
    # Audio/ML
    print("\n🎧 Audio & ML:")
    all_good &= check_package('librosa')
    all_good &= check_package('numpy')
    all_good &= check_package('whisper', 'whisper')
    
    # YouTube integration
    print("\n📺 YouTube Integration:")
    all_good &= check_package('yt-dlp', 'yt_dlp')
    all_good &= check_package('google-api-python-client', 'googleapiclient')
    all_good &= check_package('google-auth')
    all_good &= check_package('google-auth-oauthlib')
    
    # Data processing
    print("\n📈 Data Processing:")
    all_good &= check_package('pandas')
    all_good &= check_package('scipy')
    
    # Results
    print("\n" + "=" * 50)
    if all_good:
        print("✅ ALL DEPENDENCIES OK - Ready to run!")
        print("\n🚀 Run: python app.py")
    else:
        print("❌ MISSING DEPENDENCIES - Install missing packages")
        print("\n📆 Run: pip install -r requirements_webapp.txt")
        print("🔧 Also ensure FFmpeg is installed and in PATH")
    
    return all_good

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
