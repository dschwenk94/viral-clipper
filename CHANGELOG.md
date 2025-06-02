# Changelog

All notable changes to Clippy will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-06-01

### Added
- Full Flask web application with WebSocket support for real-time updates
- ASS (Advanced SubStation) caption format support with rich styling
- SRT caption format with enhanced features
- Real-time caption editing interface with live preview
- YouTube OAuth integration for direct uploads
- Speaker-specific color coding in captions
- Pop-out animation effects for captions
- Viral word highlighting with custom colors
- Background video regeneration while maintaining UI responsiveness
- Diagnostic tools for troubleshooting caption issues
- Comprehensive error handling and logging
- Caption fragment detection and merging
- Multiple speaker support (up to 3 speakers)
- Automatic speaker detection and assignment
- Video refresh functionality without losing edits

### Changed
- Reduced minimum caption duration from 0.8s to 0.3s for better sync
- Reduced minimum gap between captions from 0.15s to 0.05s
- Improved caption timing algorithm to preserve natural speech rhythm
- Enhanced speaker detection accuracy
- Optimized video processing pipeline
- Updated UI with better visual feedback
- Improved error messages and user guidance

### Fixed
- Caption timing drift issue where edited captions would progressively desynchronize
- Regex escape error in viral word formatting (`bad escape \c at position 1`)
- Fragmented caption merging for single-word or broken captions
- Caption overlap prevention algorithm
- Memory leaks in video processing
- WebSocket connection stability
- File path handling for cross-platform compatibility

### Security
- Added proper OAuth token storage
- Implemented secure file handling
- Added input validation for all user inputs
- Excluded sensitive files from version control

## [0.1.0] - 2025-05-30

### Added
- Initial skeleton implementation
- Basic project structure
- Core viral clipper module
- Enhanced heuristic peak detector
- Basic web interface templates
- Frontend static files (HTML, CSS, JS)
- Requirements and setup instructions
- MIT License

### Known Issues
- No actual functionality implemented
- Missing caption systems
- No YouTube integration
- Placeholder functions only

---

## Upgrade Instructions

### From 0.1.0 to 1.0.0
See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for detailed upgrade instructions.

Key points:
1. This is a complete rewrite - backup your data first
2. New dependencies need to be installed
3. OAuth reconfiguration required for YouTube uploads
4. Apply timing fixes for existing captions
