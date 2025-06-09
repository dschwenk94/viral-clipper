# 🎯 Clippy - AI-Powered Viral Clip Generator

Transform long-form YouTube videos into viral shorts with AI-powered speaker detection, dynamic captions, and seamless YouTube upload integration.

> **🚀 New: Multi-User Support!** Clippy now supports multiple users with individual Google accounts and YouTube channels. See [Multi-User Setup Guide](MULTIUSER_README.md) for details.

## ✨ Features

### Core Functionality
- **🤖 Auto-Peak Detection**: AI identifies the most engaging moments in videos
- **👥 Speaker Detection & Switching**: Dynamically crops video to focus on current speaker
- **📝 Smart Captions**: Phrase-by-phrase captions with speaker-specific colors
- **✏️ Real-time Caption Editing**: Edit captions with instant preview
- **📤 YouTube Integration**: One-click upload to YouTube Shorts with OAuth
- **🔄 Live Updates**: Real-time progress tracking via WebSocket

### Recent Improvements (June 2025)
- ✅ **Fixed caption timing drift** - Captions now stay perfectly synced
- ✅ **Fixed regex escape errors** - Viral word formatting works reliably
- ✅ **Enhanced ASS caption system** - Better speaker color support
- ✅ **Improved fragmented caption handling** - Smarter caption merging

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- FFmpeg installed and in PATH
- (Optional) Google Cloud Project with YouTube Data API v3 enabled

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

**Multi-User Version (Default - Recommended):**
```bash
python app_multiuser.py
```

**Single-User Version (Legacy):**
```bash
python app.py
```

Access the web interface at: `http://localhost:5000`

> **Note:** The multi-user version requires PostgreSQL and Google OAuth setup. To become a beta tester for the multi-user version, please reach out to [@dschwenk94](https://github.com/dschwenk94).

## 📖 Usage

### Basic Workflow
1. **Enter YouTube URL**: Paste any YouTube video link
2. **Set Time Range**: Choose start/end times or use auto-detection
3. **Generate Clip**: AI finds speakers and creates optimal short
4. **Edit Captions**: Adjust text and speaker assignments
5. **Upload to YouTube**: One-click upload with metadata

### Advanced Features
- **Manual Time Selection**: Override AI detection with specific timestamps
- **Speaker Assignment**: Manually assign caption colors to different speakers
- **Viral Word Highlighting**: Automatically emphasizes engaging words
- **Caption Timing Adjustment**: Fine-tune caption display timing

## 🔧 Configuration

### OAuth Setup
For YouTube upload functionality:
1. Click "🔑 Authenticate with YouTube" in the web interface
2. Complete OAuth flow in browser
3. Credentials are saved in `token.pickle` for future use

### File Structure
```
Clippy/
├── app.py                              # Main Flask application
├── auto_peak_viral_clipper.py          # Core clip generation engine
├── enhanced_heuristic_peak_detector.py # AI moment detection
├── ass_caption_update_system_v2.py     # Fixed caption system
├── srt_viral_caption_system.py         # SRT caption support
├── static/                             # Frontend assets
├── templates/                          # HTML templates
├── clips/                              # Generated clips (auto-created)
├── downloads/                          # Video cache (auto-created)
└── client_secrets.json                 # OAuth credentials (you create)
```

## 🎥 Supported Formats

### Input
- Any public YouTube video
- Recommended: Videos with clear speech and multiple speakers

### Output
- **Video**: MP4 (H.264) optimized for social media
- **Aspect Ratio**: 9:16 (vertical) for Shorts/Reels/TikTok
- **Captions**: Burned-in with customizable styling
- **Duration**: Configurable (default 30 seconds)

## 🛠️ API Endpoints

- `POST /api/generate_clip` - Start clip generation
- `GET /api/job_status/<job_id>` - Check processing status
- `POST /api/update_captions` - Update and regenerate captions
- `POST /api/upload_to_youtube` - Upload to YouTube
- `GET /api/oauth/status` - Check authentication status

## 🐛 Troubleshooting

### Common Issues

**FFmpeg not found**
```bash
# Verify installation
ffmpeg -version
# Add to PATH if needed
```

**Caption timing issues**
- Run `python apply_caption_hotfix.py` to apply latest fixes
- Ensure you're using `ass_caption_update_system_v2.py`

**OAuth authentication fails**
- Verify `client_secrets.json` exists and is valid
- Check YouTube Data API v3 is enabled in Google Cloud Console
- Delete `token.pickle` and re-authenticate

**Video download fails**
- Check YouTube URL is valid and video is public
- Update yt-dlp: `pip install --upgrade yt-dlp`

## 🏗️ Architecture

### Backend Components
- **Flask + SocketIO**: Web framework with real-time updates
- **Whisper**: OpenAI's speech recognition for transcription
- **OpenCV**: Face detection and video processing
- **FFmpeg**: Video encoding and caption burning
- **yt-dlp**: YouTube video downloading

### Caption Systems
- **ASS (Advanced SubStation)**: Primary format with rich styling
- **SRT**: Fallback format for compatibility

### Processing Pipeline
1. Download video segment
2. Detect speakers using face recognition
3. Transcribe audio with Whisper
4. Generate phrase-level captions
5. Create speaker-switching video
6. Burn in styled captions
7. Optimize for social media

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## ⚠️ Legal Notice

- Ensure you have rights to use content you're clipping
- Respect YouTube's Terms of Service
- Consider fair use guidelines for derivative content
- Always credit original creators

## 🙏 Acknowledgments

- **OpenAI Whisper** for transcription capabilities
- **FFmpeg** for video processing
- **yt-dlp** community for YouTube downloading
- All contributors and testers

---

**Built with ❤️ for content creators** | [Report Issues](https://github.com/dschwenk94/Clippy/issues) | [Migration Guide](MIGRATION_GUIDE.md)
