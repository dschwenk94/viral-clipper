# Changelog

All notable changes to the Clippy project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-06-06

### 🎉 Major Release - Multi-User Support

This release transforms Clippy into a multi-user application with individual authentication and isolated workspaces.

### Added
- **Multi-User Authentication**: Google OAuth integration for individual user accounts
- **PostgreSQL Database**: User management, session tracking, and upload history
- **Per-User YouTube Integration**: Each user connects their own YouTube account
- **Upload History**: Track all uploads per user with timestamps and metadata
- **Secure Session Management**: 7-day sessions with encrypted tokens
- **User Isolation**: Complete separation of jobs, clips, and uploads between users
- **Beta Testing System**: Controlled access during development phase

### Changed
- Default app is now `app_multiuser.py` (single-user version preserved as `app.py`)
- OAuth scopes expanded to include user profile information
- WebSocket rooms now user-specific for isolated real-time updates
- File structure reorganized with new `auth/` and `database/` modules

### Security
- All OAuth tokens encrypted using Fernet symmetric encryption
- Database credentials stored in environment variables
- Session tokens use cryptographically secure random generation
- CSRF protection in OAuth flow

### Technical Details
- New dependencies: `psycopg2-binary`, `python-dotenv`
- Database schema: `users`, `upload_history`, `user_sessions` tables
- Migration system for database updates
- Comprehensive error handling for OAuth flows

### Notes
- Beta access required (contact @dschwenk94 for access)
- PostgreSQL required for multi-user mode
- Single-user version remains available for simpler deployments

## [1.0.0] - 2025-06-01

### 🎉 Major Release - Full Implementation

This release transforms Clippy from a basic skeleton into a fully functional viral clip generator with advanced AI features.

### Added
- **Web Interface**: Complete Flask-based web application with real-time updates
- **Auto-Peak Detection**: AI-powered algorithm to find the most engaging moments
- **Speaker Detection**: Automatic face detection and tracking for dynamic video cropping
- **ASS Caption System**: Advanced subtitle format with speaker colors and effects
- **SRT Caption Support**: Alternative caption format for compatibility
- **Caption Editor**: Real-time caption editing with instant preview
- **YouTube Integration**: OAuth-based direct upload to YouTube Shorts
- **WebSocket Support**: Live progress updates during processing
- **Phrase-Level Captions**: Intelligent caption breaking for readability
- **Viral Word Detection**: Automatic highlighting of engaging words
- **Multiple Speaker Support**: Up to 3 speakers with distinct colors

### Fixed
- **Caption Timing Drift**: Captions now stay perfectly synchronized throughout the video
- **Regex Escape Error**: Fixed "bad escape \c" error in viral word formatting
- **Fragment Caption Handling**: Improved merging of single-letter captions
- **Memory Management**: Better cleanup of temporary files
- **Path Resolution**: Fixed absolute path issues in FFmpeg commands

### Changed
- Migrated from basic file structure to full Flask application
- Switched primary caption format from SRT to ASS for better styling
- Improved speaker assignment algorithm
- Enhanced error handling throughout the application
- Updated all dependencies to latest stable versions

### Technical Improvements
- Reduced MIN_CAPTION_DURATION from 0.8s to 0.3s
- Reduced MIN_GAP_BETWEEN_CAPTIONS from 0.15s to 0.05s
- Implemented smart timing preservation algorithm
- Added comprehensive logging system
- Improved video processing pipeline efficiency

## [0.1.0] - 2025-05-30

### Initial Skeleton Release
- Basic project structure
- Core module placeholders
- Initial documentation
- Basic dependencies list

---

## Future Roadmap

### Planned for v1.1.0
- [ ] Batch processing for multiple clips
- [ ] Cloud storage integration
- [ ] Advanced analytics dashboard
- [ ] Mobile-responsive UI improvements
- [ ] Additional language support

### Planned for v2.0.0
- [ ] TikTok direct upload
- [ ] Instagram Reels integration
- [ ] AI content suggestions
- [ ] Collaborative editing features
- [ ] Plugin system for extensions
