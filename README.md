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

### Multi-User Features (NEW!)
- **🔐 Google OAuth Authentication**: Secure sign-in with Google accounts
- **👤 Individual User Workspaces**: Each user gets their own isolated environment
- **📊 Personal Upload History**: Track your YouTube uploads
- **🔒 Encrypted Token Storage**: Secure storage of OAuth credentials
- **🎯 Session Management**: Persistent login with secure sessions
- **📈 User-Specific Analytics**: View your clip generation stats

### Recent Improvements (June 2025)
- ✅ **Multi-user authentication system** - Support for multiple users
- ✅ **Fixed caption timing drift** - Captions now stay perfectly synced
- ✅ **Fixed regex escape errors** - Viral word formatting works reliably
- ✅ **Enhanced ASS caption system** - Better speaker color support
- ✅ **Improved fragmented caption handling** - Smarter caption merging

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- FFmpeg installed and in PATH
- Google Cloud Project with YouTube Data API v3 enabled
- PostgreSQL 12+ (for multi-user version)

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

4. **Set up Google OAuth**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create/select a project
   - Enable YouTube Data API v3
   - Create OAuth 2.0 credentials (Web Application)
   - Add redirect URI: `http://localhost:5000/api/auth/callback`
   - Download credentials as `client_secrets.json` in project root

### Running the App

**Multi-User Version (Recommended):**
```bash
# First-time setup
python setup_multiuser.py

# Run the app
python app_multiuser.py
```

**Single-User Version (Legacy):**
```bash
python app.py
```

Access the web interface at: `http://localhost:5000`

> **Note:** Multi-user version requires PostgreSQL and additional setup. See [Multi-User Setup Guide](MULTIUSER_README.md) for detailed instructions.

## 📖 Usage

### Multi-User Workflow
1. **Sign In**: Click "Sign in with Google" on the home page
2. **Authenticate**: Complete Google OAuth flow
3. **Generate Clips**: Create clips that are tied to your account
4. **Upload to YouTube**: Upload directly to your YouTube channel
5. **View History**: See all your previous uploads

### Basic Clip Generation
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

### Multi-User Setup
1. **Database Configuration**
   ```bash
   # Create PostgreSQL database
   createdb clippy
   
   # Set environment variables in .env
   DB_NAME=clippy
   DB_USER=your_user
   DB_PASSWORD=your_password
   ```

2. **OAuth Configuration**
   - Set up Web Application credentials in Google Cloud Console
   - Add authorized redirect URI
   - Enable test users during development

### File Structure
```
Clippy/
├── app.py                              # Single-user Flask application
├── app_multiuser.py                    # Multi-user Flask application
├── auth/                               # Authentication modules
│   ├── decorators.py                   # Auth decorators
│   ├── models.py                       # User models
│   ├── oauth_manager.py                # OAuth flow handler
│   └── token_manager.py                # Token encryption
├── database/                           # Database modules
│   ├── connection.py                   # DB connection pool
│   └── migrate.py                      # Migration runner
├── migrations/                         # Database migrations
├── auto_peak_viral_clipper.py          # Core clip generation engine
├── enhanced_heuristic_peak_detector.py # AI moment detection
├── ass_caption_update_system_v2.py     # Fixed caption system
├── srt_viral_caption_system.py         # SRT caption support
├── static/                             # Frontend assets
│   ├── script.js                       # Single-user JavaScript
│   └── script_multiuser.js             # Multi-user JavaScript
├── templates/                          # HTML templates
│   ├── index.html                      # Single-user interface
│   ├── index_multiuser.html            # Multi-user interface
│   └── auth_error.html                 # Auth error page
├── clips/                              # Generated clips (auto-created)
├── downloads/                          # Video cache (auto-created)
├── .env.example                        # Environment template
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

### Authentication (Multi-User)
- `GET /api/auth/status` - Check authentication status
- `GET /api/auth/login` - Initiate OAuth flow
- `GET /api/auth/callback` - OAuth callback handler
- `POST /api/auth/logout` - Logout current user

### Clip Generation
- `POST /api/generate_clip` - Start clip generation
- `GET /api/job_status/<job_id>` - Check processing status
- `POST /api/update_captions` - Update and regenerate captions
- `POST /api/upload_to_youtube` - Upload to YouTube
- `GET /api/upload_history` - Get user's upload history

## 🐛 Troubleshooting

### Common Issues

**"No encryption key provided" (Multi-User)**
- Set `TOKEN_ENCRYPTION_KEY` in .env file
- Generate key: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

**Database connection failed (Multi-User)**
- Ensure PostgreSQL is running: `pg_isready`
- Check credentials in .env file
- Run migrations: `python migrations/001_initial_setup.py`

**FFmpeg not found**
```bash
# Verify installation
ffmpeg -version
# Add to PATH if needed
```

**OAuth authentication fails**
- Verify `client_secrets.json` exists and is valid
- Check YouTube Data API v3 is enabled
- For multi-user: Ensure redirect URI matches configuration
- For beta testing: Ensure your email is added as a test user

**Caption timing issues**
- Run `python apply_caption_hotfix.py` to apply latest fixes
- Ensure you're using `ass_caption_update_system_v2.py`

## 🏗️ Architecture

### Backend Components
- **Flask + SocketIO**: Web framework with real-time updates
- **PostgreSQL**: User data and session storage (multi-user)
- **Whisper**: OpenAI's speech recognition for transcription
- **OpenCV**: Face detection and video processing
- **FFmpeg**: Video encoding and caption burning
- **yt-dlp**: YouTube video downloading

### Security Features (Multi-User)
- **OAuth 2.0**: Secure authentication with Google
- **Token Encryption**: Fernet symmetric encryption for stored tokens
- **Session Management**: Secure session tokens with expiration
- **User Isolation**: Complete separation of user data and jobs

### Processing Pipeline
1. User authenticates (multi-user only)
2. Download video segment
3. Detect speakers using face recognition
4. Transcribe audio with Whisper
5. Generate phrase-level captions
6. Create speaker-switching video
7. Burn in styled captions
8. Upload to user's YouTube channel

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
- Multi-user version: Each user is responsible for their own content

## 🙏 Acknowledgments

- **OpenAI Whisper** for transcription capabilities
- **FFmpeg** for video processing
- **yt-dlp** community for YouTube downloading
- All contributors and testers

---

**Built with ❤️ for content creators** | [Report Issues](https://github.com/dschwenk94/Clippy/issues) | [Multi-User Guide](MULTIUSER_README.md) | [Migration Guide](MIGRATION_GUIDE.md)
