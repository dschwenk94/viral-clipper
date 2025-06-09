// 🎯 Viral Clipper JavaScript - MULTI-USER VERSION WITH TIKTOK INTEGRATION
// Allows clip generation without authentication, prompts for auth only on upload

class TikTokIntegration {
    constructor(app) {
        this.app = app;
        this.isConnected = false;
        this.currentUploadJob = null;
    }
    
    async checkConnection() {
        try {
            const response = await fetch('/api/auth/platforms');
            const data = await response.json();
            
            if (data.connected && data.connected.tiktok) {
                this.isConnected = data.connected.tiktok.connected;
                this.updateConnectionUI(data.connected.tiktok);
            }
            
            return this.isConnected;
        } catch (error) {
            console.error('Failed to check TikTok connection:', error);
            return false;
        }
    }
    
    updateConnectionUI(connectionInfo) {
        const tiktokSection = document.getElementById('tiktok-connection');
        if (!tiktokSection) return;
        
        if (this.isConnected) {
            tiktokSection.innerHTML = `
                <div class="platform-connected">
                    <div class="platform-info">
                        <span class="platform-icon">🎵</span>
                        <span>TikTok: @${connectionInfo.username || 'Connected'}</span>
                    </div>
                    <button class="disconnect-btn" onclick="viralClipperApp.tiktokIntegration.disconnect()">
                        Disconnect
                    </button>
                </div>
            `;
        } else {
            tiktokSection.innerHTML = `
                <div class="platform-disconnected">
                    <div class="platform-info">
                        <span class="platform-icon">🎵</span>
                        <span>TikTok: Not connected</span>
                    </div>
                    <button class="connect-btn" onclick="viralClipperApp.tiktokIntegration.connect()">
                        Connect TikTok
                    </button>
                </div>
            `;
        }
    }
    
    async connect() {
        try {
            const response = await fetch('/api/auth/connect/tiktok');
            const result = await response.json();
            
            if (result.authorization_url) {
                // Open TikTok auth in new window
                const authWindow = window.open(
                    result.authorization_url,
                    'TikTok Authorization',
                    'width=500,height=700'
                );
                
                // Check for completion
                const checkInterval = setInterval(() => {
                    if (authWindow.closed) {
                        clearInterval(checkInterval);
                        // Refresh connection status
                        this.checkConnection();
                        this.app.showSuccess('TikTok connection process completed');
                    }
                }, 1000);
            } else {
                this.app.showError('Failed to initiate TikTok connection');
            }
        } catch (error) {
            console.error('TikTok connection error:', error);
            this.app.showError('Failed to connect TikTok');
        }
    }
    
    async disconnect() {
        if (!confirm('Are you sure you want to disconnect your TikTok account?')) {
            return;
        }
        
        try {
            const response = await fetch('/api/auth/disconnect/tiktok', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.isConnected = false;
                this.updateConnectionUI({});
                this.app.showSuccess('TikTok account disconnected');
            } else {
                this.app.showError(result.error || 'Failed to disconnect TikTok');
            }
        } catch (error) {
            console.error('TikTok disconnect error:', error);
            this.app.showError('Failed to disconnect TikTok');
        }
    }
    
    showUploadOptions() {
        // Add TikTok upload option to the upload screen
        const platformSelector = document.getElementById('upload-platform');
        if (!platformSelector) return;
        
        if (this.isConnected) {
            // Add TikTok option if not already present
            if (!platformSelector.querySelector('option[value="tiktok"]')) {
                const option = document.createElement('option');
                option.value = 'tiktok';
                option.textContent = 'TikTok';
                platformSelector.appendChild(option);
            }
        } else {
            // Remove TikTok option if present
            const tiktokOption = platformSelector.querySelector('option[value="tiktok"]');
            if (tiktokOption) {
                tiktokOption.remove();
            }
        }
    }
    
    showTikTokUploadForm() {
        const uploadForm = document.getElementById('platform-upload-form');
        if (!uploadForm) return;
        
        uploadForm.innerHTML = `
            <h3 class="card-title">Upload to TikTok</h3>
            
            <div class="form-group">
                <label class="form-label" for="tiktok-title">Title *</label>
                <div class="input-with-counter">
                    <input type="text" 
                           id="tiktok-title" 
                           class="form-input" 
                           placeholder="Enter video title (max 150 chars)" 
                           maxlength="150" 
                           required>
                    <div class="char-counter">0 / 150</div>
                </div>
            </div>
            
            <div class="form-group">
                <label class="form-label" for="tiktok-description">Description</label>
                <div class="input-with-counter">
                    <textarea id="tiktok-description" 
                              class="form-input" 
                              placeholder="Add description with #hashtags and @mentions" 
                              rows="4" 
                              maxlength="2200"></textarea>
                    <div class="char-counter">0 / 2200</div>
                </div>
            </div>
            
            <div class="form-group">
                <label class="form-label">Privacy Settings</label>
                <div class="option-group">
                    <div class="option-item">
                        <input type="radio" id="tiktok-public" name="tiktok-privacy" value="PUBLIC_TO_EVERYONE" checked>
                        <label for="tiktok-public">Public</label>
                    </div>
                    <div class="option-item">
                        <input type="radio" id="tiktok-friends" name="tiktok-privacy" value="MUTUAL_FOLLOW_FRIENDS">
                        <label for="tiktok-friends">Friends Only</label>
                    </div>
                    <div class="option-item">
                        <input type="radio" id="tiktok-private" name="tiktok-privacy" value="SELF_ONLY">
                        <label for="tiktok-private">Private</label>
                    </div>
                </div>
            </div>
            
            <div class="form-group">
                <label class="form-label">Interaction Settings</label>
                <div class="option-group">
                    <div class="option-item">
                        <input type="checkbox" id="tiktok-allow-comments" checked>
                        <label for="tiktok-allow-comments">Allow comments</label>
                    </div>
                    <div class="option-item">
                        <input type="checkbox" id="tiktok-allow-duet" checked>
                        <label for="tiktok-allow-duet">Allow Duet</label>
                    </div>
                    <div class="option-item">
                        <input type="checkbox" id="tiktok-allow-stitch" checked>
                        <label for="tiktok-allow-stitch">Allow Stitch</label>
                    </div>
                </div>
            </div>
            
            <div class="form-group">
                <label class="form-label">Upload Mode</label>
                <div class="option-group">
                    <div class="option-item">
                        <input type="radio" id="tiktok-draft" name="tiktok-mode" value="draft" checked>
                        <label for="tiktok-draft">Save to Drafts (Review in TikTok app)</label>
                    </div>
                    <div class="option-item">
                        <input type="radio" id="tiktok-direct" name="tiktok-mode" value="direct">
                        <label for="tiktok-direct">Post Directly</label>
                    </div>
                </div>
            </div>
            
            <div class="caption-actions" style="margin-top: 2rem;">
                <button class="btn btn-ghost" onclick="viralClipperApp.showScreen(2)">
                    <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
                    </svg>
                    Back to Edit
                </button>
                <button class="btn btn-primary" onclick="viralClipperApp.tiktokIntegration.upload()">
                    <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                    </svg>
                    Upload to TikTok
                </button>
            </div>
            
            <div id="tiktok-upload-status" class="status-message"></div>
        `;
        
        // Add character counters
        this.setupCharCounters();
    }
    
    setupCharCounters() {
        const titleInput = document.getElementById('tiktok-title');
        const descInput = document.getElementById('tiktok-description');
        
        if (titleInput) {
            const counter = titleInput.parentElement.querySelector('.char-counter');
            titleInput.addEventListener('input', (e) => {
                const count = e.target.value.length;
                counter.textContent = `${count} / 150`;
                if (count >= 140) {
                    counter.classList.add('warning');
                } else {
                    counter.classList.remove('warning');
                }
            });
        }
        
        if (descInput) {
            const counter = descInput.parentElement.querySelector('.char-counter');
            descInput.addEventListener('input', (e) => {
                const count = e.target.value.length;
                counter.textContent = `${count} / 2200`;
                if (count >= 2000) {
                    counter.classList.add('warning');
                } else {
                    counter.classList.remove('warning');
                }
            });
        }
    }
    
    async upload() {
        const title = document.getElementById('tiktok-title').value.trim();
        const description = document.getElementById('tiktok-description').value.trim();
        const privacyLevel = document.querySelector('input[name="tiktok-privacy"]:checked').value;
        const allowComments = document.getElementById('tiktok-allow-comments').checked;
        const allowDuet = document.getElementById('tiktok-allow-duet').checked;
        const allowStitch = document.getElementById('tiktok-allow-stitch').checked;
        const uploadMode = document.querySelector('input[name="tiktok-mode"]:checked').value;
        
        if (!title) {
            this.app.showError('Title is required for TikTok');
            return;
        }
        
        if (!this.app.currentJobId) {
            this.app.showError('No clip available for upload');
            return;
        }
        
        try {
            const uploadStatus = document.getElementById('tiktok-upload-status');
            uploadStatus.className = 'upload-status';
            uploadStatus.innerHTML = '🔄 Starting TikTok upload...';
            uploadStatus.classList.remove('hidden');
            
            const response = await fetch('/api/upload_to_tiktok', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    job_id: this.app.currentJobId,
                    title: title,
                    description: description,
                    privacy_level: privacyLevel,
                    allow_comments: allowComments,
                    allow_duet: allowDuet,
                    allow_stitch: allowStitch,
                    upload_mode: uploadMode
                })
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.currentUploadJob = result.upload_job_id;
                uploadStatus.innerHTML = '🔄 Uploading to TikTok...';
                
                // Socket.io will handle progress updates
            } else {
                uploadStatus.className = 'upload-status error';
                uploadStatus.innerHTML = `❌ ${result.error}`;
                
                if (response.status === 401) {
                    // TikTok not connected
                    setTimeout(() => {
                        if (confirm('TikTok account not connected. Would you like to connect now?')) {
                            this.connect();
                        }
                    }, 1000);
                }
            }
        } catch (error) {
            console.error('TikTok upload error:', error);
            const uploadStatus = document.getElementById('tiktok-upload-status');
            uploadStatus.className = 'upload-status error';
            uploadStatus.innerHTML = '❌ Network error occurred';
        }
    }
    
    handleUploadProgress(data) {
        if (data.upload_job_id !== this.currentUploadJob) return;
        
        const uploadStatus = document.getElementById('tiktok-upload-status');
        if (uploadStatus) {
            uploadStatus.innerHTML = `🔄 ${data.message} (${data.progress}%)`;
        }
    }
    
    handleUploadComplete(data) {
        if (data.upload_job_id !== this.currentUploadJob) return;
        
        const uploadStatus = document.getElementById('tiktok-upload-status');
        if (uploadStatus) {
            uploadStatus.className = 'upload-status success';
            uploadStatus.innerHTML = `
                ✅ ${data.message}<br>
                ${data.share_url ? `<a href="${data.share_url}" target="_blank" class="video-link">View on TikTok</a>` : ''}
            `;
        }
        
        this.currentUploadJob = null;
        
        // Load TikTok history
        this.loadUploadHistory();
    }
    
    handleUploadError(data) {
        if (data.upload_job_id !== this.currentUploadJob) return;
        
        const uploadStatus = document.getElementById('tiktok-upload-status');
        if (uploadStatus) {
            uploadStatus.className = 'upload-status error';
            uploadStatus.innerHTML = `❌ Upload failed: ${data.error}`;
        }
        
        this.currentUploadJob = null;
    }
    
    async loadUploadHistory() {
        try {
            const response = await fetch('/api/tiktok/upload_history');
            if (!response.ok) return;
            
            const result = await response.json();
            
            if (result.uploads && result.uploads.length > 0) {
                const historySection = document.getElementById('tiktok-upload-history');
                if (historySection) {
                    let html = '<h4>Recent TikTok Uploads</h4><div class="upload-history-list">';
                    
                    result.uploads.slice(0, 5).forEach(upload => {
                        const uploadDate = new Date(upload.uploaded_at).toLocaleDateString();
                        const statusIcon = upload.upload_type === 'direct' ? '📺' : '📝';
                        html += `
                            <div class="upload-history-item">
                                ${upload.share_url ? 
                                    `<a href="${upload.share_url}" target="_blank" class="upload-link">
                                        ${statusIcon} ${upload.title}
                                    </a>` :
                                    `<span>${statusIcon} ${upload.title} (${upload.upload_type})</span>`
                                }
                                <span class="upload-date">${uploadDate}</span>
                            </div>
                        `;
                    });
                    
                    html += '</div>';
                    historySection.innerHTML = html;
                }
            }
        } catch (error) {
            console.error('Failed to load TikTok history:', error);
        }
    }
}

class ViralClipperApp {
    constructor() {
        this.socket = io();
        this.currentJobId = null;
        this.currentClipData = null;
        this.currentScreen = 1;
        this.currentUser = null;
        this.sessionId = null;
        
        // Initialize TikTok integration
        this.tiktokIntegration = new TikTokIntegration(this);
        
        this.checkAuthStatus();
        this.initializeEventListeners();
        this.initializeSocketListeners();
    }

    async checkAuthStatus() {
        try {
            const response = await fetch('/api/auth/status');
            const result = await response.json();
            
            this.currentUser = result.authenticated ? result.user : null;
            this.sessionId = result.session_id;
            
            // Update UI but don't force authentication
            this.updateAuthUI();
            
            // Show anonymous clips count if not authenticated
            if (!this.currentUser && result.anonymous_clips_count > 0) {
                this.showAnonymousClipsNotice(result.anonymous_clips_count);
            }
            
            // Check for recent clips after authentication
            if (this.currentUser) {
                this.checkForRecentClips();
                // Check TikTok connection
                this.tiktokIntegration.checkConnection();
            }
            
        } catch (error) {
            console.error('Auth check failed:', error);
            this.currentUser = null;
            this.updateAuthUI();
        }
    }
    
    async checkForRecentClips() {
        // Check localStorage for recent job ID
        const recentJobId = localStorage.getItem('recent_job_id');
        if (recentJobId) {
            try {
                const response = await fetch(`/api/job_status/${recentJobId}`);
                if (response.ok) {
                    const result = await response.json();
                    if (result.status === 'completed' && result.clip_data) {
                        // Restore the clip
                        this.currentJobId = recentJobId;
                        this.currentClipData = result.clip_data;
                        
                        // Show notification
                        this.showSuccess('Your clip has been restored!');
                        
                        // Load the editor screen
                        this.loadClipEditor(result.clip_data, result.clip_data.captions);
                        this.showScreen(2);
                        
                        // Clear from localStorage
                        localStorage.removeItem('recent_job_id');
                    }
                }
            } catch (error) {
                console.error('Failed to restore clip:', error);
                localStorage.removeItem('recent_job_id');
            }
        }
    }

    updateAuthUI() {
        const authSection = document.getElementById('auth-section');
        const mainApp = document.getElementById('main-app');
        const userInfo = document.getElementById('user-info');
        
        // Always show main app - authentication is optional
        authSection.style.display = 'none';
        mainApp.style.display = 'block';
        
        if (this.currentUser) {
            // User is authenticated - show profile
            userInfo.innerHTML = `
                <div class="user-profile">
                    ${this.currentUser.picture_url ? 
                        `<img src="${this.currentUser.picture_url}" alt="Profile" class="user-avatar">` : 
                        '<div class="user-avatar">👤</div>'
                    }
                    <span class="user-name">${this.currentUser.name || this.currentUser.email}</span>
                </div>
                <button class="btn btn-ghost btn-sm" id="logout-btn">Logout</button>
            `;
            
            // Add logout listener
            document.getElementById('logout-btn').addEventListener('click', () => this.logout());
            
            // Load upload history
            this.loadUploadHistory();
            
            // Load platform connections
            this.loadPlatformConnections();
            
        } else {
            // User is not authenticated - show sign in button
            userInfo.innerHTML = `
                <button class="btn btn-secondary btn-sm" id="header-signin-btn">
                    <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M17.64 9.20454C17.64 8.56636 17.5827 7.95272 17.4764 7.36363H9V10.845H13.8436C13.635 11.97 13.0009 12.9231 12.0477 13.5613V15.8195H14.9564C16.6582 14.2527 17.64 11.9454 17.64 9.20454Z" fill="#4285F4"/>
                        <path d="M9 18C11.43 18 13.4673 17.1941 14.9564 15.8195L12.0477 13.5613C11.2418 14.1013 10.2109 14.4204 9 14.4204C6.65591 14.4204 4.67182 12.8372 3.96409 10.71H0.957275V13.0418C2.43818 15.9831 5.48182 18 9 18Z" fill="#34A853"/>
                        <path d="M3.96409 10.71C3.78409 10.17 3.68182 9.59318 3.68182 9C3.68182 8.40682 3.78409 7.83 3.96409 7.29V4.95818H0.957275C0.347727 6.17318 0 7.54773 0 9C0 10.4523 0.347727 11.8268 0.957275 13.0418L3.96409 10.71Z" fill="#FBBC05"/>
                        <path d="M9 3.57955C10.3214 3.57955 11.5077 4.03364 12.4405 4.92545L15.0218 2.34409C13.4632 0.891818 11.4259 0 9 0C5.48182 0 2.43818 2.01682 0.957275 4.95818L3.96409 7.29C4.67182 5.16273 6.65591 3.57955 9 3.57955Z" fill="#EA4335"/>
                    </svg>
                    Sign in with Google
                </button>
            `;
            
            // Add sign in listener
            document.getElementById('header-signin-btn').addEventListener('click', () => this.signInWithGoogle());
        }
    }

    showAnonymousClipsNotice(count) {
        const notice = document.createElement('div');
        notice.className = 'anonymous-clips-notice';
        notice.innerHTML = `
            <div class="notice-content">
                <span>💡 You have ${count} unsaved clip${count > 1 ? 's' : ''}. Sign in to save them to your account!</span>
                <button class="sign-in-link">Sign in now</button>
            </div>
        `;
        
        const container = document.querySelector('.container');
        container.insertBefore(notice, container.firstChild);
        
        notice.querySelector('.sign-in-link').addEventListener('click', () => {
            this.signInWithGoogle();
        });
    }

    initializeEventListeners() {
        // Form submission - no auth required
        document.getElementById('clipForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.generateClip();
        });

        // Navigation buttons
        document.getElementById('continue-to-upload-btn').addEventListener('click', () => {
            this.continueToUpload();
        });

        document.getElementById('back-to-edit-btn').addEventListener('click', () => {
            this.showScreen(2);
        });

        document.getElementById('back-to-input-btn').addEventListener('click', () => {
            this.backToInput();
        });

        // Caption editing
        document.getElementById('update-captions-btn').addEventListener('click', () => {
            this.updateCaptions();
        });

        // Upload - requires auth
        document.getElementById('upload-btn').addEventListener('click', () => {
            this.uploadToYouTube();
        });

        // Error modal
        document.getElementById('close-error-btn').addEventListener('click', () => {
            document.getElementById('error-modal').classList.add('hidden');
        });
    }

    initializeSocketListeners() {
        this.socket.on('progress_update', (data) => {
            this.updateProgress(data);
        });

        this.socket.on('clip_completed', (data) => {
            this.handleClipCompleted(data);
        });

        this.socket.on('regeneration_update', (data) => {
            this.handleRegenerationUpdate(data);
        });

        this.socket.on('regeneration_complete', (data) => {
            this.handleRegenerationComplete(data);
        });

        this.socket.on('regeneration_error', (data) => {
            this.handleRegenerationError(data);
        });

        this.socket.on('upload_progress', (data) => {
            this.updateUploadProgress(data);
        });

        // TikTok socket listeners
        this.socket.on('tiktok_upload_progress', (data) => {
            this.tiktokIntegration.handleUploadProgress(data);
        });

        this.socket.on('tiktok_upload_complete', (data) => {
            this.tiktokIntegration.handleUploadComplete(data);
        });

        this.socket.on('tiktok_upload_error', (data) => {
            this.tiktokIntegration.handleUploadError(data);
        });

        this.socket.on('connect', () => {
            console.log('Connected to server');
        });
        
        this.socket.on('connected', (data) => {
            console.log('Joined room:', data.room, 'Type:', data.type);
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from server');
        });
    }

    async signInWithGoogle() {
        try {
            const response = await fetch('/api/auth/login');
            const result = await response.json();
            
            if (result.authorization_url) {
                // Redirect to Google OAuth
                window.location.href = result.authorization_url;
            } else {
                this.showError('Failed to initiate authentication');
            }
            
        } catch (error) {
            console.error('Sign in error:', error);
            this.showError('Authentication failed');
        }
    }

    async logout() {
        try {
            const response = await fetch('/api/auth/logout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (response.ok) {
                this.currentUser = null;
                this.updateAuthUI();
                this.showSuccess('Logged out successfully');
                
                // Reload to reset state
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            }
            
        } catch (error) {
            console.error('Logout error:', error);
            this.showError('Logout failed');
        }
    }

    async loadUploadHistory() {
        try {
            const response = await fetch('/api/upload_history');
            if (!response.ok) return;
            
            const result = await response.json();
            
            if (result.uploads && result.uploads.length > 0) {
                const historySection = document.getElementById('upload-history');
                if (historySection) {
                    let html = '<h4>Recent Uploads</h4><div class="upload-history-list">';
                    
                    result.uploads.slice(0, 5).forEach(upload => {
                        const uploadDate = new Date(upload.uploaded_at).toLocaleDateString();
                        html += `
                            <div class="upload-history-item">
                                <a href="${upload.url}" target="_blank" class="upload-link">
                                    📹 ${upload.title}
                                </a>
                                <span class="upload-date">${uploadDate}</span>
                            </div>
                        `;
                    });
                    
                    html += '</div>';
                    historySection.innerHTML = html;
                }
            }
            
            // Also check for recent clips
            this.loadRecentClips();
            
        } catch (error) {
            console.error('Failed to load upload history:', error);
        }
    }
    
    async loadRecentClips() {
        try {
            const response = await fetch('/api/user_clips');
            if (!response.ok) return;
            
            const result = await response.json();
            
            if ((result.converted_clips && result.converted_clips.length > 0) || 
                (result.active_clips && result.active_clips.length > 0)) {
                
                // Show a notice about available clips
                const notice = document.createElement('div');
                notice.className = 'recent-clips-notice';
                notice.innerHTML = `
                    <div class="notice-content">
                        <span>🎬 You have recent clips available!</span>
                        <button class="view-clips-btn">View Clips</button>
                    </div>
                `;
                
                const container = document.querySelector('.container');
                const existingNotice = container.querySelector('.recent-clips-notice');
                if (existingNotice) {
                    existingNotice.remove();
                }
                container.insertBefore(notice, container.firstChild);
                
                notice.querySelector('.view-clips-btn').addEventListener('click', () => {
                    this.showRecentClipsModal(result);
                });
            }
            
        } catch (error) {
            console.error('Failed to load recent clips:', error);
        }
    }
    
    showRecentClipsModal(clipsData) {
        // Create modal to show recent clips
        const modal = document.createElement('div');
        modal.className = 'clips-modal-overlay';
        
        let clipsHtml = '';
        
        // Show active clips
        if (clipsData.active_clips && clipsData.active_clips.length > 0) {
            clipsHtml += '<h3>Active Clips</h3>';
            clipsData.active_clips.forEach(clip => {
                clipsHtml += `
                    <div class="clip-item">
                        <span>📹 ${clip.video_url}</span>
                        <button class="restore-clip-btn" data-job-id="${clip.job_id}">Restore</button>
                    </div>
                `;
            });
        }
        
        // Show converted clips
        if (clipsData.converted_clips && clipsData.converted_clips.length > 0) {
            clipsHtml += '<h3>Previous Clips</h3>';
            clipsData.converted_clips.forEach(clip => {
                const createdDate = new Date(clip.created_at).toLocaleDateString();
                clipsHtml += `
                    <div class="clip-item">
                        <span>📹 ${clip.video_url}</span>
                        <span class="clip-date">${createdDate}</span>
                    </div>
                `;
            });
        }
        
        modal.innerHTML = `
            <div class="clips-modal">
                <h2>Your Recent Clips</h2>
                <div class="clips-list">
                    ${clipsHtml}
                </div>
                <button class="close-modal-btn">Close</button>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Add event listeners
        modal.querySelectorAll('.restore-clip-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const jobId = e.target.dataset.jobId;
                localStorage.setItem('recent_job_id', jobId);
                window.location.reload();
            });
        });
        
        modal.querySelector('.close-modal-btn').addEventListener('click', () => {
            modal.remove();
        });
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }

    async generateClip() {
        // No authentication check - anyone can generate clips
        const formData = new FormData(document.getElementById('clipForm'));
        const data = {
            url: formData.get('url'),
            duration: parseInt(formData.get('duration')),
            start_time: formData.get('start_time') || null,
            end_time: formData.get('end_time') || null
        };

        // Validate inputs
        if (!this.validateInputs(data)) {
            return;
        }

        try {
            this.showProgressScreen();
            
            const response = await fetch('/api/generate_clip', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                this.currentJobId = result.job_id;
                console.log('Clip generation started:', result.job_id);
                
                if (result.is_anonymous) {
                    console.log('Generating clip anonymously');
                }
                
                // Start polling as backup in case WebSocket fails
                this.startJobPolling();
            } else {
                this.showError(result.error || 'Failed to start clip generation');
                this.showScreen(1);
            }
        } catch (error) {
            console.error('Generate clip error:', error);
            this.showError('Network error occurred');
            this.showScreen(1);
        }
    }
    
    startJobPolling() {
        // Poll job status every 2 seconds as a backup
        this.pollingInterval = setInterval(async () => {
            if (!this.currentJobId) {
                clearInterval(this.pollingInterval);
                return;
            }
            
            try {
                const response = await fetch(`/api/job_status/${this.currentJobId}`);
                const result = await response.json();
                
                if (response.ok) {
                    console.log('Job status:', result.status, result.progress + '%');
                    
                    this.updateProgress({
                        job_id: this.currentJobId,
                        status: result.status,
                        progress: result.progress,
                        message: result.message
                    });
                    
                    if (result.status === 'completed' && result.clip_data) {
                        clearInterval(this.pollingInterval);
                        this.handleClipCompleted({
                            job_id: this.currentJobId,
                            clip_data: result.clip_data,
                            captions: result.clip_data.captions
                        });
                    } else if (result.status === 'error') {
                        clearInterval(this.pollingInterval);
                    }
                }
            } catch (error) {
                console.error('Polling error:', error);
            }
        }, 2000);
    }

    continueToUpload() {
        // Check if user is authenticated before showing upload screen
        if (!this.currentUser) {
            this.showAuthPrompt();
        } else {
            this.showScreen(3);
            // Update TikTok options
            this.tiktokIntegration.showUploadOptions();
        }
    }

    showAuthPrompt() {
        // Create a custom auth prompt overlay
        const authPrompt = document.createElement('div');
        authPrompt.className = 'auth-prompt-overlay';
        authPrompt.innerHTML = `
            <div class="auth-prompt-modal">
                <h2>Sign in to Upload</h2>
                <p>To upload your clip to YouTube or TikTok, you need to sign in with your Google account.</p>
                
                <div class="auth-benefits">
                    <h4>Benefits of signing in:</h4>
                    <ul>
                        <li>📤 Upload directly to YouTube and TikTok</li>
                        <li>📊 Track your upload history</li>
                        <li>💾 Save your clips to your account</li>
                        <li>🔄 Access your clips from anywhere</li>
                    </ul>
                </div>
                
                <div class="auth-prompt-actions">
                    <button class="google-signin-btn" id="auth-prompt-signin">
                        <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M17.64 9.20454C17.64 8.56636 17.5827 7.95272 17.4764 7.36363H9V10.845H13.8436C13.635 11.97 13.0009 12.9231 12.0477 13.5613V15.8195H14.9564C16.6582 14.2527 17.64 11.9454 17.64 9.20454Z" fill="white"/>
                            <path d="M9 18C11.43 18 13.4673 17.1941 14.9564 15.8195L12.0477 13.5613C11.2418 14.1013 10.2109 14.4204 9 14.4204C6.65591 14.4204 4.67182 12.8372 3.96409 10.71H0.957275V13.0418C2.43818 15.9831 5.48182 18 9 18Z" fill="white"/>
                            <path d="M3.96409 10.71C3.78409 10.17 3.68182 9.59318 3.68182 9C3.68182 8.40682 3.78409 7.83 3.96409 7.29V4.95818H0.957275C0.347727 6.17318 0 7.54773 0 9C0 10.4523 0.347727 11.8268 0.957275 13.0418L3.96409 10.71Z" fill="white"/>
                            <path d="M9 3.57955C10.3214 3.57955 11.5077 4.03364 12.4405 4.92545L15.0218 2.34409C13.4632 0.891818 11.4259 0 9 0C5.48182 0 2.43818 2.01682 0.957275 4.95818L3.96409 7.29C4.67182 5.16273 6.65591 3.57955 9 3.57955Z" fill="white"/>
                        </svg>
                        Sign in with Google
                    </button>
                    <button class="action-btn secondary" id="auth-prompt-cancel">
                        Stay on Edit Screen
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(authPrompt);
        
        // Add event listeners
        document.getElementById('auth-prompt-signin').addEventListener('click', () => {
            this.signInWithGoogle();
        });
        
        document.getElementById('auth-prompt-cancel').addEventListener('click', () => {
            authPrompt.remove();
        });
        
        // Close on background click
        authPrompt.addEventListener('click', (e) => {
            if (e.target === authPrompt) {
                authPrompt.remove();
            }
        });
    }

    handlePlatformChange(platform) {
        if (platform === 'youtube') {
            // Show YouTube form
            document.getElementById('platform-upload-form').innerHTML = document.getElementById('youtube-upload-form').innerHTML;
        } else if (platform === 'tiktok') {
            // Show TikTok form
            this.tiktokIntegration.showTikTokUploadForm();
        }
    }

    validateInputs(data) {
        // URL validation
        if (!data.url || (!data.url.includes('youtube.com') && !data.url.includes('youtu.be'))) {
            this.showError('Please enter a valid YouTube URL');
            return false;
        }

        // Duration validation
        if (data.duration < 10 || data.duration > 60) {
            this.showError('Duration must be between 10 and 60 seconds');
            return false;
        }

        // Time validation
        if (data.start_time && data.end_time) {
            const startSeconds = this.parseTimeToSeconds(data.start_time);
            const endSeconds = this.parseTimeToSeconds(data.end_time);
            
            if (startSeconds === null || endSeconds === null) {
                this.showError('Invalid time format. Use MM:SS or seconds');
                return false;
            }
            
            if (startSeconds >= endSeconds) {
                this.showError('End time must be after start time');
                return false;
            }
        }

        return true;
    }

    parseTimeToSeconds(timeStr) {
        if (!timeStr) return null;
        
        timeStr = timeStr.trim();
        
        if (timeStr.includes(':')) {
            const parts = timeStr.split(':');
            if (parts.length === 2) {
                const minutes = parseInt(parts[0]);
                const seconds = parseInt(parts[1]);
                if (!isNaN(minutes) && !isNaN(seconds)) {
                    return minutes * 60 + seconds;
                }
            }
        } else {
            const seconds = parseFloat(timeStr);
            if (!isNaN(seconds)) {
                return seconds;
            }
        }
        
        return null;
    }

    showProgressScreen() {
        this.showScreen('progress');
        this.resetProgressSteps();
    }

    // Update progress UI with circular progress
updateProgress(data) {
    const progressCircle = document.getElementById('progress-circle');
    const progressPercentage = document.getElementById('progress-percentage');
    const progressMessage = document.getElementById('progress-message');

    // Update circular progress
    const circumference = 2 * Math.PI * 90; // radius = 90
    const offset = circumference - (data.progress / 100) * circumference;
    progressCircle.style.strokeDashoffset = offset;

    progressPercentage.textContent = `${data.progress}%`;
    progressMessage.textContent = data.message;

    // Update progress steps
    this.updateProgressSteps(data.progress, data.message);

    if (data.status === 'error') {
        this.showError(data.message);
        this.showScreen(1);
    }
}

    updateProgressSteps(progress, message) {
        const steps = document.querySelectorAll('.progress-step');
        
        // Reset all steps
        steps.forEach(step => {
            step.classList.remove('active', 'completed');
        });

        // Activate steps based on progress
        if (progress >= 20) {
            document.getElementById('step-download').classList.add('active');
        }
        if (progress >= 40) {
            document.getElementById('step-download').classList.add('completed');
            document.getElementById('step-analyze').classList.add('active');
        }
        if (progress >= 60) {
            document.getElementById('step-analyze').classList.add('completed');
            document.getElementById('step-speakers').classList.add('active');
        }
        if (progress >= 80) {
            document.getElementById('step-speakers').classList.add('completed');
            document.getElementById('step-captions').classList.add('active');
        }
        if (progress >= 90) {
            document.getElementById('step-captions').classList.add('completed');
            document.getElementById('step-video').classList.add('active');
        }
        if (progress >= 100) {
            document.getElementById('step-video').classList.add('completed');
        }
    }

    resetProgressSteps() {
        const steps = document.querySelectorAll('.progress-step');
        steps.forEach(step => {
            step.classList.remove('active', 'completed');
        });
        
        // Reset circular progress
        const progressCircle = document.getElementById('progress-circle');
        if (progressCircle) {
            const circumference = 2 * Math.PI * 90;
            progressCircle.style.strokeDashoffset = circumference;
        }
        
        const progressPercentage = document.getElementById('progress-percentage');
        const progressMessage = document.getElementById('progress-message');
        if (progressPercentage) progressPercentage.textContent = '0%';
        if (progressMessage) progressMessage.textContent = 'Initializing...';
    }

    handleClipCompleted(data) {
        this.currentClipData = data.clip_data;
        
        // Save job ID to localStorage in case of page refresh/auth redirect
        if (this.currentJobId) {
            localStorage.setItem('recent_job_id', this.currentJobId);
        }
        
        this.loadClipEditor(data.clip_data, data.captions);
        this.showScreen(2);
    }

    loadClipEditor(clipData, captions) {
        // Load video
        const video = document.getElementById('clip-video');
        const videoSource = document.getElementById('video-source');
        const filename = clipData.path.split('/').pop();
        videoSource.src = `/clips/${filename}`;
        video.load();

        // Show detection info
        this.displayDetectionInfo(clipData);

        // Load captions
        this.loadCaptions(captions);

        // Pre-populate upload form
        this.prepareUploadForm(clipData);
    }

    displayDetectionInfo(clipData) {
        const detectionDetails = document.getElementById('detection-details');
        
        const startTime = clipData.optimal_timestamp;
        const endTime = startTime + clipData.duration;
        const startMMS = this.formatSecondsToMMSS(startTime);
        const endMMS = this.formatSecondsToMMSS(endTime);
        
        let html = `
            <div class="info-item">
                <div class="info-label">Timing</div>
                <div class="info-value">${startMMS} - ${endMMS}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Confidence</div>
                <div class="info-value">${clipData.detection_confidence.toFixed(2)}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Detection</div>
                <div class="info-value">${clipData.auto_detected ? 'AI Auto' : 'Manual'}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Speakers</div>
                <div class="info-value">${clipData.video_speakers} detected</div>
            </div>
        `;

        detectionDetails.innerHTML = html;
    }

    loadCaptions(captions) {
        const captionsEditor = document.getElementById('captions-editor');
        
        if (!captions || captions.length === 0) {
            captionsEditor.innerHTML = '<p class="text-muted">No captions available</p>';
            return;
        }

        let html = '';
        captions.forEach((caption, index) => {
            const speakerNum = this.getSpeakerNumber(caption.speaker);
            const speakerClass = `speaker-${speakerNum}`;
            
            html += `
                <div class="caption-item" data-index="${index}">
                    <div class="caption-controls">
                        <select class="speaker-selector ${speakerClass}" data-index="${index}">
                            <option value="1" ${speakerNum === 1 ? 'selected' : ''}>Speaker 1</option>
                            <option value="2" ${speakerNum === 2 ? 'selected' : ''}>Speaker 2</option>
                            <option value="3" ${speakerNum === 3 ? 'selected' : ''}>Speaker 3</option>
                        </select>
                    </div>
                    <textarea class="caption-text-input" 
                             data-index="${index}" 
                             placeholder="Edit caption text..."
                             rows="2">${caption.text}</textarea>
                </div>
            `;
        });

        captionsEditor.innerHTML = html;
        
        // Add event listeners
        document.querySelectorAll('.speaker-selector').forEach(select => {
            select.addEventListener('change', (e) => this.handleSpeakerChange(e));
        });
        
        // Auto-resize textareas
        document.querySelectorAll('.caption-text-input').forEach(textarea => {
            textarea.addEventListener('input', (e) => {
                e.target.style.height = 'auto';
                e.target.style.height = e.target.scrollHeight + 'px';
            });
            // Initial resize
            textarea.style.height = 'auto';
            textarea.style.height = textarea.scrollHeight + 'px';
        });
    }

    async updateCaptions() {
        if (!this.currentJobId || !this.currentClipData) {
            this.showError('No clip data available');
            return;
        }

        const captionItems = document.querySelectorAll('.caption-item');
        const updatedCaptions = Array.from(captionItems).map(item => {
            const index = item.dataset.index;
            const textInput = item.querySelector('.caption-text-input');
            const speakerSelect = item.querySelector('.speaker-selector');
            
            return {
                index: parseInt(index),
                text: textInput.value,
                speaker: `Speaker ${speakerSelect.value}`
            };
        });

        try {
            const response = await fetch('/api/update_captions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    job_id: this.currentJobId,
                    captions: updatedCaptions
                })
            });

            const result = await response.json();

            if (response.ok) {
                this.showSuccess('Captions update started!');
                this.showRegenerationProgress();
            } else {
                this.showError(result.error || 'Failed to update captions');
            }
        } catch (error) {
            console.error('Update captions error:', error);
            this.showError('Network error occurred');
        }
    }

    prepareUploadForm(clipData) {
        const titleField = document.getElementById('video-title');
        const descriptionField = document.getElementById('video-description');

        if (!titleField.value) {
            titleField.value = this.generateSuggestedTitle(clipData);
        }

        if (!descriptionField.value) {
            descriptionField.value = this.generateSuggestedDescription(clipData);
        }
    }

    generateSuggestedTitle(clipData) {
        const originalTitle = clipData.original_title || 'Viral Clip';
        const shortTitle = originalTitle.length > 50 ? originalTitle.substring(0, 47) + '...' : originalTitle;
        return `${shortTitle} - Viral Moment`;
    }

    generateSuggestedDescription(clipData) {
        let description = `Viral clip generated from: ${clipData.original_title || 'Original Video'}\n\n`;
        
        if (clipData.auto_detected) {
            description += `Auto-detected at ${(clipData.optimal_timestamp / 60).toFixed(1)} min\n`;
        }
        
        description += `\n#Shorts #Viral #Clips`;
        
        return description;
    }

    async uploadToYouTube() {
        // Check authentication first
        if (!this.currentUser) {
            this.showAuthPrompt();
            return;
        }

        const title = document.getElementById('video-title').value.trim();
        const description = document.getElementById('video-description').value.trim();
        const privacyStatus = document.querySelector('input[name="privacy-status"]:checked').value;
        
        if (!title) {
            this.showError('Title is required');
            return;
        }

        if (!this.currentJobId) {
            this.showError('No clip available for upload');
            return;
        }

        try {
            const uploadStatus = document.getElementById('upload-status');
            uploadStatus.className = 'upload-status';
            uploadStatus.innerHTML = '🔄 Uploading to YouTube...';

            const response = await fetch('/api/upload_to_youtube', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    job_id: this.currentJobId,
                    title: title,
                    description: description,
                    privacy_status: privacyStatus
                })
            });

            const result = await response.json();

            if (response.ok) {
                uploadStatus.className = 'upload-status success';
                uploadStatus.innerHTML = `
                    ✅ ${result.message}<br>
                    <a href="${result.url}" target="_blank" class="video-link">View on YouTube</a>
                `;
                
                // Reload upload history
                this.loadUploadHistory();
            } else {
                uploadStatus.className = 'upload-status error';
                uploadStatus.innerHTML = `❌ ${result.error}`;
                
                // If auth error, show auth prompt
                if (response.status === 401 || response.status === 403) {
                    setTimeout(() => {
                        this.showAuthPrompt();
                    }, 1500);
                }
            }
        } catch (error) {
            console.error('Upload error:', error);
            const uploadStatus = document.getElementById('upload-status');
            uploadStatus.className = 'upload-status error';
            uploadStatus.innerHTML = '❌ Network error occurred';
        }
    }

    updateUploadProgress(data) {
        const uploadStatus = document.getElementById('upload-status');
        if (uploadStatus && data.progress) {
            uploadStatus.innerHTML = `🔄 Uploading to YouTube... ${data.progress}%`;
        }
    }

    showScreen(screenNumber) {
        document.querySelectorAll('.screen').forEach(screen => {
            screen.classList.remove('active');
        });

        const targetScreen = screenNumber === 'progress' ? 
            document.getElementById('progress-screen') :
            document.getElementById(`screen${screenNumber}`);
        
        if (targetScreen) {
            targetScreen.classList.add('active');
            this.currentScreen = screenNumber;
            
            // Update TikTok options when showing upload screen
            if (screenNumber === 3) {
                this.tiktokIntegration.showUploadOptions();
                this.initializePlatformTabs();
                // Show YouTube form by default
                this.showPlatformUploadForm('youtube');
            }
        }
    }
    
    initializePlatformTabs() {
        const tabs = document.querySelectorAll('.platform-tab');
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                // Remove active from all tabs
                tabs.forEach(t => t.classList.remove('active'));
                // Add active to clicked tab
                tab.classList.add('active');
                // Show appropriate form
                const platform = tab.dataset.platform;
                this.selectedPlatform = platform;
                this.showPlatformUploadForm(platform);
            });
        });
    }
    
    showPlatformUploadForm(platform) {
        const formContainer = document.getElementById('platform-upload-form');
        
        if (platform === 'youtube') {
            formContainer.innerHTML = `
                <h3 class="card-title">Upload to YouTube</h3>
                
                <div class="form-group">
                    <label class="form-label" for="video-title">Video Title</label>
                    <div class="input-with-counter">
                        <input type="text" 
                               id="video-title" 
                               class="form-input" 
                               placeholder="Enter your YouTube Short title..." 
                               maxlength="100" 
                               required>
                        <div class="char-counter">0 / 100</div>
                    </div>
                </div>
                
                <div class="form-group">
                    <label class="form-label" for="video-description">Description</label>
                    <div class="input-with-counter">
                        <textarea id="video-description" 
                                  class="form-input" 
                                  placeholder="Add a description for your Short...\n\n#Shorts #Viral" 
                                  rows="6" 
                                  maxlength="5000"></textarea>
                        <div class="char-counter">0 / 5000</div>
                    </div>
                    <div class="form-hint">Include relevant hashtags for better reach</div>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Privacy Settings</label>
                    <div class="option-group">
                        <div class="option-item">
                            <input type="radio" id="private" name="privacy-status" value="private" checked>
                            <label for="private">Private (only you can see)</label>
                        </div>
                        <div class="option-item">
                            <input type="radio" id="unlisted" name="privacy-status" value="unlisted">
                            <label for="unlisted">Unlisted (anyone with link)</label>
                        </div>
                        <div class="option-item">
                            <input type="radio" id="public" name="privacy-status" value="public">
                            <label for="public">Public (everyone can see)</label>
                        </div>
                    </div>
                </div>
                
                <div class="caption-actions" style="margin-top: 2rem;">
                    <button class="btn btn-ghost" onclick="viralClipperApp.showScreen(2)">
                        <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
                        </svg>
                        Back to Edit
                    </button>
                    <button id="upload-btn" class="btn btn-primary" onclick="viralClipperApp.uploadToYouTube()">
                        <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                        </svg>
                        Upload to YouTube
                    </button>
                </div>
                
                <div id="upload-status" class="status-message"></div>
            `;
            
            // Setup character counters
            this.setupYouTubeCharCounters();
        } else if (platform === 'tiktok') {
            this.tiktokIntegration.showTikTokUploadForm();
        }
    }

    setupYouTubeCharCounters() {
        const titleInput = document.getElementById('video-title');
        const descInput = document.getElementById('video-description');
        
        if (titleInput) {
            const counter = titleInput.parentElement.querySelector('.char-counter');
            titleInput.addEventListener('input', (e) => {
                const count = e.target.value.length;
                counter.textContent = `${count} / 100`;
                if (count >= 90) {
                    counter.classList.add('warning');
                } else {
                    counter.classList.remove('warning');
                }
            });
        }
        
        if (descInput) {
            const counter = descInput.parentElement.querySelector('.char-counter');
            descInput.addEventListener('input', (e) => {
                const count = e.target.value.length;
                counter.textContent = `${count} / 5000`;
            });
        }
    }

    async loadPlatformConnections() {
        try {
            const response = await fetch('/api/auth/platforms');
            const data = await response.json();
            
            const connectionsDiv = document.getElementById('platform-connections');
            if (!connectionsDiv) return;
            
            let html = '<h3 class="card-title" style="margin-bottom: 1rem;">Platform Connections</h3>';
            html += '<div class="platform-connections">';
            
            // YouTube connection
            const youtubeConnected = data.connected && data.connected.youtube;
            html += `
                <div class="platform-connection-card ${youtubeConnected ? 'connected' : 'disconnected'}">
                    <div class="platform-info">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="#FF0000">
                            <path d="M10 15l5.19-3L10 9v6m11.56-7.83c.13.47.22 1.1.28 1.9.07.8.1 1.49.1 2.09L22 12c0 2.19-.16 3.8-.44 4.83-.25.9-.83 1.48-1.73 1.73-.47.13-1.33.22-2.65.28-1.3.07-2.49.1-3.59.1L12 19c-4.19 0-6.8-.16-7.83-.44-.9-.25-1.48-.83-1.73-1.73-.13-.47-.22-1.1-.28-1.9-.07-.8-.1-1.49-.1-2.09L2 12c0-2.19.16-3.8.44-4.83.25-.9.83-1.48 1.73-1.73.47-.13 1.33-.22 2.65-.28 1.3-.07 2.49-.1 3.59-.1L12 5c4.19 0 6.8.16 7.83.44.9.25 1.48.83 1.73 1.73z"/>
                        </svg>
                        <span>YouTube ${youtubeConnected ? '✓' : ''}</span>
                    </div>
                    ${!youtubeConnected ? '<span class="text-muted">Sign in to connect</span>' : ''}
                </div>
            `;
            
            // TikTok connection
            const tiktokConnected = data.connected && data.connected.tiktok && data.connected.tiktok.connected;
            html += `
                <div class="platform-connection-card ${tiktokConnected ? 'connected' : 'disconnected'}">
                    <div class="platform-info">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="#000000">
                            <path d="M16.6 5.82s.51.5 0 0A4.278 4.278 0 0 1 15.54 3h-3.09v12.4a2.592 2.592 0 0 1-2.59 2.5c-1.42 0-2.6-1.16-2.6-2.6c0-1.72 1.66-3.01 3.37-2.48V9.66c-3.45-.46-6.47 2.22-6.47 5.64c0 3.33 2.76 5.7 5.69 5.7c3.14 0 5.69-2.55 5.69-5.7V9.01a7.35 7.35 0 0 0 4.3 1.38V7.3s-1.88.09-3.24-1.48z"/>
                        </svg>
                        <span>TikTok ${tiktokConnected ? '✓' : ''}</span>
                    </div>
                    ${tiktokConnected ? 
                        `<button class="btn btn-ghost btn-sm" onclick="viralClipperApp.tiktokIntegration.disconnect()">Disconnect</button>` : 
                        `<button class="btn btn-secondary btn-sm" onclick="viralClipperApp.tiktokIntegration.connect()">Connect</button>`
                    }
                </div>
            `;
            
            html += '</div>';
            connectionsDiv.innerHTML = html;
            
        } catch (error) {
            console.error('Failed to load platform connections:', error);
        }
    }

    showError(message) {
        document.getElementById('error-message').textContent = message;
        document.getElementById('error-modal').classList.remove('hidden');
    }

    showSuccess(message) {
        // Simple success notification
        const notification = document.createElement('div');
        notification.className = 'success-notification';
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
    
    getSpeakerNumber(speakerName) {
        if (speakerName.toLowerCase().includes('speaker 1')) {
            return 1;
        } else if (speakerName.toLowerCase().includes('speaker 2')) {
            return 2;
        } else if (speakerName.toLowerCase().includes('speaker 3')) {
            return 3;
        }
        return 1;
    }
    
    handleSpeakerChange(event) {
        const select = event.target;
        const newSpeakerNum = parseInt(select.value);
        select.className = `speaker-selector speaker-${newSpeakerNum}`;
    }
    
    async backToInput() {
        try {
            if (this.currentJobId) {
                await fetch('/api/back_to_input', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        job_id: this.currentJobId
                    })
                });
            }
            
            this.currentJobId = null;
            this.currentClipData = null;
            document.getElementById('clipForm').reset();
            this.showScreen(1);
            
        } catch (error) {
            console.error('Back to input error:', error);
        }
    }
    
    formatSecondsToMMSS(seconds) {
        const minutes = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${minutes}:${secs.toString().padStart(2, '0')}`;
    }
    
    showRegenerationProgress() {
        const captionActions = document.querySelector('.caption-actions');
        
        let regenProgress = captionActions.querySelector('.regeneration-progress');
        if (!regenProgress) {
            regenProgress = document.createElement('div');
            regenProgress.className = 'regeneration-progress';
            regenProgress.innerHTML = `
                <div class="regen-status">
                    <span class="regen-text">Regenerating video...</span>
                    <div class="regen-progress-bar">
                        <div class="regen-progress-fill" style="width: 0%"></div>
                    </div>
                </div>
            `;
            captionActions.appendChild(regenProgress);
        }
    }
    
    handleRegenerationUpdate(data) {
        const regenProgress = document.querySelector('.regeneration-progress');
        if (regenProgress) {
            const progressFill = regenProgress.querySelector('.regen-progress-fill');
            const progressText = regenProgress.querySelector('.regen-text');
            
            if (progressFill) {
                progressFill.style.width = `${data.progress}%`;
            }
            
            if (progressText) {
                progressText.textContent = data.message;
            }
        }
    }
    
    handleRegenerationComplete(data) {
        const regenProgress = document.querySelector('.regeneration-progress');
        if (regenProgress) {
            regenProgress.remove();
        }
        
        this.showSuccess('Video regenerated successfully!');
        this.refreshVideo();
    }
    
    handleRegenerationError(data) {
        const regenProgress = document.querySelector('.regeneration-progress');
        if (regenProgress) {
            regenProgress.remove();
        }
        
        this.showError(`Regeneration failed: ${data.error}`);
    }
    
    async refreshVideo() {
        if (!this.currentJobId) return;
        
        try {
            const response = await fetch(`/api/refresh_video/${this.currentJobId}`);
            const result = await response.json();
            
            if (response.ok) {
                this.currentClipData = result.clip_data;
                
                const video = document.getElementById('clip-video');
                const videoSource = document.getElementById('video-source');
                videoSource.src = result.video_url;
                video.load();
                
                if (result.captions) {
                    this.loadCaptions(result.captions);
                }
            }
        } catch (error) {
            console.error('Refresh video error:', error);
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.viralClipperApp = new ViralClipperApp();
});
