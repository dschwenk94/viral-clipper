# 🎯 Clippy - AI-Powered YouTube Shorts Generator

Transform long-form YouTube videos into viral shorts with AI-powered speaker detection, dynamic captions, and seamless YouTube upload integration.

## ✨ Features

- **🎤 Auto-Peak Detection**: AI identifies the most engaging moments in videos
- **👥 Speaker Detection & Switching**: Dynamically crops video to focus on current speaker
- **📝 Smart Captions**: Phrase-by-phrase captions with speaker-specific colors using ASS Caption System V6 (Speech Sync)
- **✏️ Real-time Caption Editing**: Edit captions with instant preview
- **📤 YouTube Integration**: One-click upload to YouTube Shorts with OAuth
- **🚀 Multi-User Support**: Multiple users with individual Google accounts

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- FFmpeg installed and in PATH
- PostgreSQL (for multi-user support)
- Google Cloud Project with YouTube Data API v3 enabled

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

3. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

Access the web interface at: `http://localhost:5000`

## 📂 Project Structure

```
Clippy/
├── app.py                    # Main application (multi-user version)
├── ass_caption_update_system_v6.py  # Speech-synced caption system
├── src/
│   ├── core/                # Core functionality
│   │   ├── auto_peak_viral_clipper.py
│   │   ├── viral_clipper_complete.py
│   │   └── enhanced_heuristic_peak_detector.py
│   └── utils/               # Utility functions
├── templates/               # HTML templates
├── static/                  # CSS, JS, assets
├── configs/                 # Configuration files
├── docs/                    # Documentation
└── archive/                 # Old versions (git ignored)
```

## 🎥 Caption System

Clippy uses the **ASS Caption Update System V6** which features:
- **Speech Synchronization**: Captions perfectly sync with original speech timing
- **Speaker Colors**: Automatic color coding for different speakers
- **Viral Word Highlighting**: Emphasizes engaging words
- **Pop-out Effects**: Dynamic caption animations

## 📖 Documentation

- [Setup Guide](docs/SETUP.md)
- [Multi-User Configuration](docs/MULTIUSER.md)
- [API Reference](docs/API.md)
- [Development Guide](docs/DEVELOPMENT.md)

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.
