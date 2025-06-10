// 🎯 Viral Clipper JavaScript - MULTI-USER VERSION
// Includes authentication flow and user-specific features

class ViralClipperApp {
    constructor() {
        this.socket = io();
        this.currentJobId = null;
        this.currentClipData = null;
        this.currentScreen = 1;
        this.currentUser = null;
        
        this.checkAuthStatus();
        this.initializeEventListeners();
        this.initializeSocketListeners();
    }

    async checkAuthStatus() {
        try {
            const response = await fetch('/api/auth/status');
            const result = await response.json();
            
            this.currentUser = result.authenticated ? result.user : null;
            this.updateAuthUI();
            
        } catch (error) {
            console.error('Auth check failed:', error);
            this.currentUser = null;
            this.updateAuthUI();
        }
    }

    updateAuthUI() {
        const authSection = document.getElementById('auth-section');
        const mainApp = document.getElementById('main-app');
        const userInfo = document.getElementById('user-info');
        
        if (this.currentUser) {
            // User is authenticated
            authSection.style.display = 'none';
            mainApp.style.display = 'block';
            
            // Show user info
            userInfo.innerHTML = `
                <div class="user-profile">
                    ${this.currentUser.picture_url ? 
                        `<img src="${this.currentUser.picture_url}" alt="Profile" class="user-avatar">` : 
                        '<div class="user-avatar-placeholder">👤</div>'
                    }
                    <span class="user-name">${this.currentUser.name || this.currentUser.email}</span>
                    <button class="logout-btn" id="logout-btn">Logout</button>
                </div>
            `;
            
            // Add logout listener
            document.getElementById('logout-btn').addEventListener('click', () => this.logout());
            
            // Check upload history
            this.loadUploadHistory();
            
        } else {
            // User needs to authenticate
            authSection.style.display = 'block';
            mainApp.style.display = 'none';
            userInfo.innerHTML = '';
        }
    }

    initializeEventListeners() {
        // Authentication
        const googleSignInBtn = document.getElementById('google-signin-btn');
        if (googleSignInBtn) {
            googleSignInBtn.addEventListener('click', () => this.signInWithGoogle());
        }

        // Form submission
        document.getElementById('clipForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.generateClip();
        });

        // Navigation buttons
        document.getElementById('continue-to-upload-btn').addEventListener('click', () => {
            this.showScreen(3);
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

        // Upload
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

        this.socket.on('connect', () => {
            console.log('Connected to server');
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
            
        } catch (error) {
            console.error('Failed to load upload history:', error);
        }
    }

    async generateClip() {
        if (!this.currentUser) {
            this.showError('Please sign in to generate clips');
            return;
        }

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

    updateProgress(data) {
        const progressFill = document.getElementById('progress-fill');
        const progressPercentage = document.getElementById('progress-percentage');
        const progressMessage = document.getElementById('progress-message');

        progressFill.style.width = `${data.progress}%`;
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
        const steps = document.querySelectorAll('.step');
        
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
        const steps = document.querySelectorAll('.step');
        steps.forEach(step => {
            step.classList.remove('active', 'completed');
        });
        
        document.getElementById('progress-fill').style.width = '0%';
        document.getElementById('progress-percentage').textContent = '0%';
        document.getElementById('progress-message').textContent = 'Initializing...';
    }

    handleClipCompleted(data) {
        this.currentClipData = data.clip_data;
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
            <div class="detection-info">
                <h4>Clip Details</h4>
                <p><strong>Timing:</strong> ${startMMS} - ${endMMS}</p>
                <p><strong>Confidence:</strong> ${clipData.detection_confidence.toFixed(2)}</p>
                <p><strong>Auto-detected:</strong> ${clipData.auto_detected ? 'Yes' : 'No'}</p>
                <p><strong>Speakers:</strong> ${clipData.video_speakers} detected</p>
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
                <div class="caption-line" data-index="${index}">
                    <select class="speaker-selector ${speakerClass}" data-index="${index}">
                        <option value="1" ${speakerNum === 1 ? 'selected' : ''}>Speaker 1</option>
                        <option value="2" ${speakerNum === 2 ? 'selected' : ''}>Speaker 2</option>
                        <option value="3" ${speakerNum === 3 ? 'selected' : ''}>Speaker 3</option>
                    </select>
                    <input type="text" class="caption-text" value="${caption.text}" 
                           data-index="${index}" placeholder="Edit caption text..." />
                </div>
            `;
        });

        captionsEditor.innerHTML = html;
        
        // Add event listeners
        document.querySelectorAll('.speaker-selector').forEach(select => {
            select.addEventListener('change', (e) => this.handleSpeakerChange(e));
        });
    }

    async updateCaptions() {
        if (!this.currentJobId || !this.currentClipData) {
            this.showError('No clip data available');
            return;
        }

        const captionLines = document.querySelectorAll('.caption-line');
        const updatedCaptions = Array.from(captionLines).map(line => {
            const index = line.dataset.index;
            const textInput = line.querySelector('.caption-text');
            const speakerSelect = line.querySelector('.speaker-selector');
            
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
