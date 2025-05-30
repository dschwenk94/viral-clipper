# 🎯 Viral Clipper - YouTube Shorts Generator

Automatically generate viral clips from long-form YouTube videos with speaker switching, dynamic captions, and seamless YouTube upload integration.

## ✨ Features

- **🤖 Auto-Peak Detection**: Intelligent identification of viral moments
- **👥 Speaker Detection**: Dynamic video cropping and speaker switching  
- **📝 Smart Captions**: Phrase-by-phrase captions with speaker-specific colors
- **🎨 Real-time Editing**: Live caption editing with instant preview
- **📤 YouTube Integration**: One-click upload to YouTube Shorts with OAuth
- **🔄 Hybrid Processing**: Live preview + background video regeneration

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- FFmpeg installed and in PATH
- Google Cloud Project with YouTube Data API v3 enabled

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/dschwenk94/viral-clipper.git
   cd viral-clipper
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements_webapp.txt
   ```

3. **Install FFmpeg**
   - **macOS**: `brew install ffmpeg`
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)
   - **Linux**: `sudo apt install ffmpeg`

4. **Set up Google OAuth** (Required for YouTube upload)
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

## 🔧 Configuration

### OAuth Setup

The app requires YouTube OAuth for uploading. On first upload:

1. Click "🔑 Authenticate with YouTube" 
2. Complete OAuth flow in browser
3. Credentials are saved for future use

### File Structure

```
viral-clipper/
├── app.py                          # Main Flask application
├── auto_peak_viral_clipper.py      # Core clip generation
├── enhanced_heuristic_peak_detector.py  # Peak detection algorithms
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

## 🔧 API Endpoints

- `POST /api/generate_clip` - Start clip generation
- `GET /api/oauth/status` - Check authentication status  
- `POST /api/oauth/authenticate` - Start OAuth flow
- `POST /api/upload_to_youtube` - Upload to YouTube
- `POST /api/update_captions` - Update captions with regeneration

## 🐛 Troubleshooting

### Common Issues

**FFmpeg not found**
```bash
# Test FFmpeg installation
ffmpeg -version
```

**OAuth authentication fails**
- Ensure `client_secrets.json` is in project root
- Check Google Cloud Console OAuth setup
- Verify YouTube Data API v3 is enabled

**Video download fails**  
- Check YouTube URL format
- Some videos may be geo-restricted
- Update yt-dlp: `pip install --upgrade yt-dlp`

## 🎯 Architecture

### Backend Components
- **Flask App** (`app.py`): Main web application with SocketIO
- **Auto-Peak Detector** (`auto_peak_viral_clipper.py`): Core clip generation
- **Peak Detection Engine** (`enhanced_heuristic_peak_detector.py`): AI moment detection
- **Speaker Systems**: Face detection, clustering, and video cropping
- **Caption Engine**: Whisper transcription with phrase-level timing

### Frontend
- **Modern UI**: Dark theme with responsive design
- **Real-time Updates**: WebSocket-powered progress tracking
- **Live Editing**: Caption editing with instant preview
- **Hybrid Approach**: Live preview + background regeneration

## 📄 License

MIT License - see LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Submit pull request

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

**Built with AI assistance** 🤖 - Automated viral moment detection powered by advanced heuristics and machine learning.
