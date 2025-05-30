# 🎯 Viral Clipper Setup Instructions

Complete setup guide for the Viral Clipper application.

## 📋 Prerequisites

### Required Software
- **Python 3.8+** - [Download from python.org](https://www.python.org/downloads/)
- **FFmpeg** - Video processing engine
- **Git** - For cloning the repository

### FFmpeg Installation

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
1. Download from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to your PATH

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Verify Installation:**
```bash
ffmpeg -version
```

## 🚀 Quick Setup

### 1. Clone Repository
```bash
git clone https://github.com/dschwenk94/viral-clipper.git
cd viral-clipper
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements_webapp.txt
```

### 4. Set Up Google OAuth (Required for YouTube Upload)

1. **Go to [Google Cloud Console](https://console.cloud.google.com/)**
2. **Create a new project** or select existing one
3. **Enable YouTube Data API v3:**
   - Go to "APIs & Services" > "Library"
   - Search for "YouTube Data API v3"
   - Click "Enable"
4. **Create OAuth 2.0 Credentials:**
   - Go to "APIs & Services" > "Credentials"
   - Click "+ CREATE CREDENTIALS" > "OAuth 2.0 Client ID"
   - Choose "Desktop Application"
   - Name it "Viral Clipper"
   - Download the credentials
5. **Save credentials file:**
   - Rename downloaded file to `client_secrets.json`
   - Place it in the project root directory

### 5. Run the Application
```bash
python app.py
```

### 6. Access the Interface
Open your browser and go to: **http://localhost:5000**

## 📁 Project Structure

```
viral-clipper/
├── app.py                          # Main Flask application
├── auto_peak_viral_clipper.py      # Core clip generation
├── enhanced_heuristic_peak_detector.py  # Peak detection
├── viral_clipper_complete.py       # Speaker detection & processing
├── storage_optimizer.py            # Smart video caching
├── client_secrets.json             # OAuth credentials (you create this)
├── requirements_webapp.txt         # Python dependencies
├── templates/
│   └── index.html                  # Web interface
├── static/
│   ├── style.css                   # Styling
│   └── script.js                   # Frontend logic
├── clips/                          # Generated clips (auto-created)
├── downloads/                      # Downloaded videos (auto-created)
└── configs/                        # Speaker configs (auto-created)
```

## 🎛️ Usage Guide

### Basic Usage
1. **Enter YouTube URL** - Paste any YouTube video URL
2. **Set Duration** - Choose clip length (10-60 seconds)
3. **Choose Timing:**
   - Leave blank for **auto-detection** (recommended)
   - Or specify manual start/end times
4. **Generate Clip** - Click the generate button
5. **Edit Captions** - Modify captions and speaker assignments
6. **Upload to YouTube** - One-click upload to YouTube Shorts

### Auto-Detection Features
- 🎵 **Audio Energy Analysis** - Finds high-energy moments
- 🎤 **Speech Pattern Detection** - Identifies engaging speech
- 📍 **Position-Based Heuristics** - Uses content-type specific timing
- 🎯 **Multi-Signal Scoring** - Combines multiple detection methods

### Advanced Features
- **Speaker Detection** - Automatic face detection and cropping
- **Dynamic Switching** - Smart cuts between speakers
- **Viral Captions** - Phrase-by-phrase captions with highlighting
- **Live Preview** - Real-time caption editing
- **Smart Caching** - Avoids re-downloading videos

## 🔧 Configuration

### Environment Variables (Optional)
```bash
# Create .env file
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your_secret_key_here
```

### YouTube Upload Settings
- **Default Privacy:** Private (safest)
- **Category:** People & Blogs
- **Format:** 1080x1920 (9:16 aspect ratio)
- **Optimization:** H.264 codec, 3Mbps video, 128kbps audio

## 🐛 Troubleshooting

### Common Issues

**"FFmpeg not found"**
```bash
# Test FFmpeg installation
ffmpeg -version

# If not found, reinstall FFmpeg and add to PATH
```

**"OAuth authentication fails"**
- Ensure `client_secrets.json` is in project root
- Check that YouTube Data API v3 is enabled in Google Cloud Console
- Verify OAuth 2.0 client is configured as "Desktop Application"

**"Video download fails"**
- Check YouTube URL format
- Some videos may be geo-restricted or private
- Update yt-dlp: `pip install --upgrade yt-dlp`

**"No module named 'cv2'"**
```bash
pip install opencv-python
```

**"Permission denied" errors**
- Run terminal/command prompt as administrator
- Check file permissions in project directory

### Debug Mode
For detailed error messages:
```bash
FLASK_DEBUG=True python app.py
```

### Logs
Check console output for detailed processing information:
- Download progress
- Peak detection results
- Speaker detection status
- Caption generation logs
- Upload progress

## 🔒 Security Notes

- **OAuth tokens** are stored locally in `token.pickle`
- **Videos default to "Private"** on YouTube for safety
- **Sensitive files** are excluded from version control
- **API credentials** should never be shared or committed

## 📈 Performance Tips

- **Use SSD storage** for faster video processing
- **Close other video applications** while processing
- **Ensure stable internet** for downloads and uploads
- **Use lower resolution source videos** for faster processing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## ⚠️ Legal Notice

- Ensure you have rights to use content you're clipping
- Respect YouTube's Terms of Service
- Consider fair use guidelines for short clips
- Add proper attribution to original creators

---

**Built with AI assistance** 🤖 - Powered by advanced heuristics and machine learning.
