# 🎯 Clippy - Viral YouTube Shorts Generator

Automatically generate viral clips from long-form YouTube videos with AI-powered speaker detection, dynamic captions, and seamless YouTube upload integration.

## ✨ Features

- **🤖 Auto-Peak Detection**: Intelligent identification of viral moments using AI heuristics
- **👥 Speaker Detection**: Dynamic video cropping and speaker switching  
- **📝 Smart Captions**: Phrase-by-phrase captions with speaker-specific colors
- **🎨 Real-time Editing**: Live caption editing with instant preview
- **📤 YouTube Integration**: One-click upload to YouTube Shorts with OAuth
- **🔄 Hybrid Processing**: Live preview + background video regeneration
- **🎬 ASS & SRT Support**: Advanced subtitle formats with rich styling

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- FFmpeg installed and in PATH
- Google Cloud Project with YouTube Data API v3 enabled (for upload feature)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/dschwenk94/Clippy.git
   cd Clippy
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements_webapp.txt
   ```

3. **Install FFmpeg**
   - **macOS**: `brew install ffmpeg`
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)
   - **Linux**: `sudo apt install ffmpeg`

4. **Set up Google OAuth** (Optional - for YouTube upload)
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create/select a project
   - Enable YouTube Data API v3
   - Create OAuth 2.0 credentials (Desktop Application)
   - Download credentials as `client_secrets.json` in project root

### Running the App

```bash
python app.py
```

Access the web interface at: `http://localhost:5000`

## 📖 Usage

1. **Generate Clip**: Enter YouTube URL and customize timing
2. **Edit Captions**: Real-time caption editing with speaker assignment
3. **Upload to YouTube**: One-click upload with OAuth authentication

## 🆕 What's New (v1.0.0 - June 2025)

### Major Features
- Full Flask web application with WebSocket support
- ASS caption system with advanced styling
- Fixed caption timing drift issues
- Real-time caption editing interface
- YouTube OAuth integration
- Improved speaker detection algorithms

### Bug Fixes
- ✅ Fixed caption synchronization drift
- ✅ Fixed regex escape errors in viral word formatting
- ✅ Fixed fragmented caption merging
- ✅ Improved caption overlap prevention

See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for upgrading from previous versions.

## 🔧 Configuration

### OAuth Setup

The app requires YouTube OAuth for uploading. On first upload:

1. Click "🔑 Authenticate with YouTube" 
2. Complete OAuth flow in browser
3. Credentials are saved for future use

### File Structure

```
Clippy/
├── app.py                          # Main Flask application
├── auto_peak_viral_clipper.py      # Core clip generation
├── enhanced_heuristic_peak_detector.py  # Peak detection algorithms
├── ass_caption_update_system_v2.py # Fixed caption system
├── srt_viral_caption_system.py    # SRT caption support
├── client_secrets.json             # OAuth credentials (create this)
├── static/                         # Frontend assets
├── templates/                      # HTML templates
├── clips/                          # Generated clips (auto-created)
├── downloads/                      # Downloaded videos (auto-created)
└── requirements_webapp.txt         # Python dependencies
```

## 🛡️ Security

- OAuth credentials are stored locally in `token.pickle`
- Videos default to "Private" upload for safety
- All sensitive files are excluded from version control

## 🎥 Features Deep Dive

### Auto-Peak Detection
- Analyzes audio energy patterns
- Identifies natural conversation breaks
- Scores moments for viral potential

### Speaker Switching
- Face detection and clustering
- Dynamic video cropping per speaker
- Smooth transitions between speakers

### Smart Captions
- Phrase-by-phrase timing
- Speaker-specific colors
- Viral word highlighting
- Real-time editing with live preview

## 🐛 Troubleshooting

### Common Issues

**FFmpeg not found**
```bash
# Test FFmpeg installation
ffmpeg -version
```

**Caption timing issues**
- Run `python apply_timing_fix.py` to apply the latest timing fixes
- See [CAPTION_TIMING_FIX.md](CAPTION_TIMING_FIX.md) for details

**OAuth authentication fails**
- Ensure `client_secrets.json` is in project root
- Check Google Cloud Console OAuth setup
- Verify YouTube Data API v3 is enabled

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## ⚠️ Legal Notice

- Ensure you have rights to use content you're clipping
- Respect YouTube's Terms of Service
- Consider fair use guidelines for short clips
- Add proper attribution to original creators

## 🔗 Links

- [YouTube Data API Documentation](https://developers.google.com/youtube/v3)
- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)
- [Flask Documentation](https://flask.palletsprojects.com/)

---

**Built with ❤️ and AI** - Making viral content creation accessible to everyone
