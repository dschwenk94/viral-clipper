// Add these TikTok-related functions to script_multiuser.js

// After the existing initialization code, add:

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
                        <span>TikTok: @${connectionInfo.username}</span>
                    </div>
                    <button class="disconnect-btn" onclick="tiktokIntegration.disconnect()">
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
                    <button class="connect-btn" onclick="tiktokIntegration.connect()">
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
            <div class="tiktok-upload-form">
                <h3>Upload to TikTok</h3>
                
                <div class="input-group">
                    <label for="tiktok-title">Title *</label>
                    <input type="text" id="tiktok-title" maxlength="150" 
                           placeholder="Enter video title (max 150 chars)" required>
                    <div class="char-count">0 / 150</div>
                </div>
                
                <div class="input-group">
                    <label for="tiktok-description">Description</label>
                    <textarea id="tiktok-description" rows="4" maxlength="2200"
                              placeholder="Add description with #hashtags and @mentions"></textarea>
                    <div class="char-count">0 / 2200</div>
                </div>
                
                <div class="upload-options">
                    <h4>Privacy Settings</h4>
                    <div class="radio-group">
                        <label class="radio-label">
                            <input type="radio" name="tiktok-privacy" value="PUBLIC_TO_EVERYONE" checked>
                            Public
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="tiktok-privacy" value="MUTUAL_FOLLOW_FRIENDS">
                            Friends Only
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="tiktok-privacy" value="SELF_ONLY">
                            Private
                        </label>
                    </div>
                </div>
                
                <div class="upload-options">
                    <h4>Interaction Settings</h4>
                    <label class="checkbox-label">
                        <input type="checkbox" id="tiktok-allow-comments" checked>
                        Allow comments
                    </label>
                    <label class="checkbox-label">
                        <input type="checkbox" id="tiktok-allow-duet" checked>
                        Allow Duet
                    </label>
                    <label class="checkbox-label">
                        <input type="checkbox" id="tiktok-allow-stitch" checked>
                        Allow Stitch
                    </label>
                </div>
                
                <div class="upload-mode">
                    <h4>Upload Mode</h4>
                    <div class="radio-group">
                        <label class="radio-label">
                            <input type="radio" name="tiktok-mode" value="draft" checked>
                            Save to Drafts (Review in TikTok app)
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="tiktok-mode" value="direct">
                            Post Directly
                        </label>
                    </div>
                </div>
                
                <div class="upload-actions">
                    <button class="action-btn primary" onclick="tiktokIntegration.upload()">
                        Upload to TikTok
                    </button>
                    <button class="action-btn secondary" onclick="viralClipperApp.showUploadPlatformSelector()">
                        Back
                    </button>
                </div>
                
                <div id="tiktok-upload-status" class="upload-status hidden"></div>
            </div>
        `;
        
        // Add character counters
        this.setupCharCounters();
    }
    
    setupCharCounters() {
        const titleInput = document.getElementById('tiktok-title');
        const descInput = document.getElementById('tiktok-description');
        
        if (titleInput) {
            titleInput.addEventListener('input', (e) => {
                const count = e.target.value.length;
                e.target.nextElementSibling.textContent = `${count} / 150`;
            });
        }
        
        if (descInput) {
            descInput.addEventListener('input', (e) => {
                const count = e.target.value.length;
                e.target.nextElementSibling.textContent = `${count} / 2200`;
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

// Initialize TikTok integration when app loads
// Add this to the ViralClipperApp constructor:
this.tiktokIntegration = new TikTokIntegration(this);

// Add socket listeners for TikTok in initializeSocketListeners:
this.socket.on('tiktok_upload_progress', (data) => {
    this.tiktokIntegration.handleUploadProgress(data);
});

this.socket.on('tiktok_upload_complete', (data) => {
    this.tiktokIntegration.handleUploadComplete(data);
});

this.socket.on('tiktok_upload_error', (data) => {
    this.tiktokIntegration.handleUploadError(data);
});

// Check for platform connection on page load
// Add to checkAuthStatus method:
if (this.currentUser) {
    this.tiktokIntegration.checkConnection();
}

// Update the upload platform selector
// Add to the showScreen method when showing screen 3:
if (screenNumber === 3) {
    this.tiktokIntegration.showUploadOptions();
}
