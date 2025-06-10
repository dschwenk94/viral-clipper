# JavaScript Files Documentation

## Current JavaScript Files in /static/

### 1. **script.js** (SINGLE-USER VERSION)
- **Used by**: `templates/index.html`
- **Purpose**: Original single-user version without authentication
- **Features**: Basic clip generation, caption editing, YouTube upload (with manual OAuth)
- **Status**: KEEP - Still used for single-user deployments

### 2. **script_multiuser.js** (IDENTICAL TO script_multiuser_anonymous.js)
- **Used by**: None currently
- **Purpose**: Multi-user version with anonymous support
- **Features**: Authentication, anonymous clip generation, user profiles
- **Status**: REDUNDANT - Same as script_multiuser_anonymous.js

### 3. **script_multiuser_anonymous.js** (ANONYMOUS SUPPORT VERSION)
- **Used by**: `templates/index_multiuser_backup.html`
- **Purpose**: Allows anonymous users to generate clips, prompts for auth on upload
- **Features**: Optional authentication, anonymous clip tracking, session management
- **Status**: KEEP - Backup version with anonymous support

### 4. **script_multiuser_original.js** (AUTHENTICATION REQUIRED VERSION)
- **Used by**: None currently
- **Purpose**: Original multi-user version that requires authentication
- **Features**: Mandatory authentication, user profiles, upload history
- **Status**: KEEP FOR REFERENCE - Shows authentication-first approach

### 5. **script_multiuser_tiktok.js** (CURRENT PRODUCTION VERSION)
- **Used by**: 
  - `templates/index_multiuser.html` (main template)
  - `templates/index_multiuser_modern.html`
- **Purpose**: Latest multi-user version with TikTok integration
- **Features**: All features from anonymous version PLUS TikTok upload support
- **Status**: KEEP - Current production version

### 6. **tiktok_integration.js**
- **Used by**: Loaded dynamically by script_multiuser_tiktok.js
- **Purpose**: TikTok-specific functionality
- **Features**: TikTok upload handling, platform switching
- **Status**: KEEP - Required for TikTok integration

## Summary

### Files to KEEP:
1. `script.js` - Single-user version
2. `script_multiuser_anonymous.js` - Anonymous support version
3. `script_multiuser_tiktok.js` - Current production version
4. `script_multiuser_original.js` - Reference implementation
5. `tiktok_integration.js` - TikTok functionality

### Files to REMOVE:
1. `script_multiuser.js` - Redundant duplicate of anonymous version

## Version History
- **v1**: script.js (single-user)
- **v2**: script_multiuser_original.js (auth required)
- **v2.5**: script_multiuser_anonymous.js (anonymous support)
- **v3**: script_multiuser_tiktok.js (adds TikTok)
