// 🎯 Viral Clipper JavaScript - FIXED VERSION - Frontend Logic
// Fixes:
// 1. Refresh button stays on caption screen with updated video
// 2. Proper state management for video updates

class ViralClipperApp {
    constructor() {
        this.socket = io();
        this.currentJobId = null;
        this.currentClipData = null;
        this.currentScreen = 1;
        
        this.initializeEventListeners();
        this.initializeSocketListeners();
    }

    initializeEventListeners() {
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

        // 🆕 NEW: Add clear all state button (for debugging)
        this.addClearStateButton();

        // Caption editing
        document.getElementById('update-captions-btn').addEventListener('click', () => {
            this.updateCaptions();
        });

        // Upload
        document.getElementById('upload-btn').addEventListener('click', () => {
            this.uploadToYouTube();
        });
        
        // OAuth buttons
        document.getElementById('authenticate-btn').addEventListener('click', () => {
            this.authenticateWithYouTube();
        });
        
        document.getElementById('test-upload-btn').addEventListener('click', () => {
            this.testYouTubeConnection();
        });
        
        document.getElementById('revoke-auth-btn').addEventListener('click', () => {
            this.revokeYouTubeAuth();
        });

        // Error modal
        document.getElementById('close-error-btn').addEventListener('click', () => {
            document.getElementById('error-modal').classList.add('hidden');
        });

        // Auto-populate title field based on original video
        document.getElementById('youtube-url').addEventListener('blur', () => {
            this.suggestTitle();
        });
    }

    initializeSocketListeners() {
        this.socket.on('progress_update', (data) => {
            this.updateProgress(data);
        });

        this.socket.on('clip_completed', (data) => {
            this.handleClipCompleted(data);
        });

        // 🆕 Hybrid approach socket listeners
        this.socket.on('regeneration_update', (data) => {
            this.handleRegenerationUpdate(data);
        });

        this.socket.on('regeneration_complete', (data) => {
            this.handleRegenerationComplete(data);
        });

        this.socket.on('regeneration_error', (data) => {
            this.handleRegenerationError(data);
        });

        this.socket.on('connect', () => {
            console.log('Connected to server');
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from server');
        });
    }

    async generateClip() {
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

        // 📝 Clear any existing state first
        console.log('🧺 CLEARING STATE: Resetting app before new clip generation');
        await this.clearAppState();

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
                console.log('🎯 NEW URL:', data.url);
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

        // Activate steps based on progress and message
        if (progress >= 20 || message.includes('Downloading')) {
            document.getElementById('step-download').classList.add('active');
        }
        if (progress >= 40 || message.includes('Analyzing')) {
            document.getElementById('step-download').classList.add('completed');
            document.getElementById('step-analyze').classList.add('active');
        }
        if (progress >= 60 || message.includes('speakers')) {
            document.getElementById('step-analyze').classList.add('completed');
            document.getElementById('step-speakers').classList.add('active');
        }
        if (progress >= 80 || message.includes('captions')) {
            document.getElementById('step-speakers').classList.add('completed');
            document.getElementById('step-captions').classList.add('active');
        }
        if (progress >= 90 || message.includes('video')) {
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
        
        // Add clip timing info
        const startTime = clipData.optimal_timestamp;
        const endTime = startTime + clipData.duration;
        const startMMS = this.formatSecondsToMMSS(startTime);
        const endMMS = this.formatSecondsToMMSS(endTime);
        const durationMMS = this.formatSecondsToMMSS(clipData.duration);
        
        let html = `
            <div class="clip-timing">
                <h4>⏱️ Clip Timing</h4>
                <div class="timing-info">
                    <div class="timing-item">
                        <div class="timing-label">Start Time</div>
                        <div class="timing-value">${startMMS}</div>
                    </div>
                    <div class="timing-item">
                        <div class="timing-label">End Time</div>
                        <div class="timing-value">${endMMS}</div>
                    </div>
                    <div class="timing-item">
                        <div class="timing-label">Duration</div>
                        <div class="timing-value">${durationMMS}</div>
                    </div>
                </div>
            </div>
            
            <div class="detection-stat">
                <strong>🎯 Confidence:</strong> ${clipData.detection_confidence.toFixed(2)}
            </div>
            <div class="detection-stat">
                <strong>🔄 Auto-detected:</strong> ${clipData.auto_detected ? 'Yes' : 'No (Manual)'}
            </div>
        `;

        if (clipData.peak_signals && clipData.peak_signals.length > 0) {
            html += `
                <div class="detection-stat">
                    <strong>🔥 Detection Signals:</strong> ${clipData.peak_signals.slice(0, 3).join(', ')}
                </div>
            `;
        }

        if (clipData.peak_reason) {
            html += `
                <div class="detection-stat">
                    <strong>💡 Reason:</strong> ${clipData.peak_reason.substring(0, 80)}...
                </div>
            `;
        }

        html += `
            <div class="detection-stat">
                <strong>👥 Speakers:</strong> ${clipData.video_speakers} detected
            </div>
            <div class="detection-stat">
                <strong>🎨 Captions:</strong> ${clipData.captions_added ? 'Added' : 'Failed'}
            </div>
        `;

        detectionDetails.innerHTML = html;
    }

    loadCaptions(captions) {
        const captionsEditor = document.getElementById('captions-editor');
        
        if (!captions || captions.length === 0) {
            captionsEditor.innerHTML = '<p class="text-muted">No captions available to edit</p>';
            return;
        }

        let html = '';
        captions.forEach((caption, index) => {
            // Determine current speaker number
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
        
        // Add event listeners for speaker changes
        document.querySelectorAll('.speaker-selector').forEach(select => {
            select.addEventListener('change', (e) => {
                this.handleSpeakerChange(e);
            });
        });
    }

    async updateCaptions() {
        if (!this.currentJobId || !this.currentClipData) {
            this.showError('No clip data available');
            return;
        }

        // Collect edited captions with speaker assignments
        const captionLines = document.querySelectorAll('.caption-line');
        const updatedCaptions = Array.from(captionLines).map(line => {
            const index = line.dataset.index || line.querySelector('[data-index]').dataset.index;
            const textInput = line.querySelector('.caption-text');
            const speakerSelect = line.querySelector('.speaker-selector');
            
            return {
                index: parseInt(index),
                text: textInput.value,
                speaker: `Speaker ${speakerSelect.value}`
            };
        });

        try {
            // 🆕 HYBRID APPROACH: Show live preview immediately
            this.showLivePreview(updatedCaptions);
            
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
                if (result.regeneration_started) {
                    this.showRegenerationProgress();
                    this.showSuccess('✨ Caption preview updated! Generating final video in background...');
                } else {
                    this.showSuccess('Captions updated successfully!');
                }
            } else {
                this.showError(result.error || 'Failed to update captions');
            }
        } catch (error) {
            console.error('Update captions error:', error);
            this.showError('Network error occurred');
        }
    }

    prepareUploadForm(clipData) {
        // Generate suggested title and description
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
        let description = `Viral clip automatically generated from: ${clipData.original_title || 'Original Video'}\n\n`;
        
        if (clipData.auto_detected) {
            description += `🎯 Auto-detected optimal moment at ${(clipData.optimal_timestamp / 60).toFixed(1)} min with ${clipData.detection_confidence.toFixed(2)} confidence\n`;
        }
        
        if (clipData.peak_signals && clipData.peak_signals.length > 0) {
            description += `🔥 Detection signals: ${clipData.peak_signals.slice(0, 3).join(', ')}\n`;
        }
        
        description += `\n#Shorts #Viral #Clips #AI #AutoGenerated`;
        
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
                    <strong>Video ID:</strong> ${result.video_id}<br>
                    <strong>Privacy:</strong> ${result.privacy_status}<br>
                    <a href="${result.url}" target="_blank" class="video-link">🔗 View on YouTube</a>
                `;
            } else {
                if (response.status === 401 && result.oauth_status) {
                    uploadStatus.className = 'upload-status error';
                    uploadStatus.innerHTML = `❌ ${result.error}<br><small>Please authenticate with YouTube first.</small>`;
                    this.updateOAuthDisplay(result.oauth_status);
                } else {
                    uploadStatus.className = 'upload-status error';
                    uploadStatus.innerHTML = `❌ ${result.error}`;
                }
            }
        } catch (error) {
            console.error('Upload error:', error);
            const uploadStatus = document.getElementById('upload-status');
            uploadStatus.className = 'upload-status error';
            uploadStatus.innerHTML = '❌ Network error occurred';
        }
    }

    suggestTitle() {
        const url = document.getElementById('youtube-url').value;
        if (url) {
            // Simple title suggestion based on URL
            const videoId = this.extractVideoId(url);
            if (videoId) {
                // This could be enhanced to fetch actual video title via API
                console.log('Video ID:', videoId);
            }
        }
    }

    extractVideoId(url) {
        const regex = /(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)/;
        const match = url.match(regex);
        return match ? match[1] : null;
    }

    showScreen(screenNumber) {
        // Hide all screens
        document.querySelectorAll('.screen').forEach(screen => {
            screen.classList.remove('active');
        });

        // Show target screen
        const targetScreen = screenNumber === 'progress' ? 
            document.getElementById('progress-screen') :
            document.getElementById(`screen${screenNumber}`);
        
        if (targetScreen) {
            targetScreen.classList.add('active');
            this.currentScreen = screenNumber;
            
            // Check OAuth status when showing upload screen
            if (screenNumber === 3) {
                this.checkOAuthStatus();
            }
        }
    }

    showError(message) {
        document.getElementById('error-message').textContent = message;
        document.getElementById('error-modal').classList.remove('hidden');
    }

    showSuccess(message) {
        // Simple success notification - could be enhanced with a proper toast
        console.log('Success:', message);
        // For now, show as alert - could be replaced with a better notification system
        alert(message);
    }
    
    getSpeakerNumber(speakerName) {
        // Extract speaker number from name
        if (speakerName.toLowerCase().includes('speaker 1') || speakerName.toLowerCase().includes('matt')) {
            return 1;
        } else if (speakerName.toLowerCase().includes('speaker 2') || speakerName.toLowerCase().includes('shane')) {
            return 2;
        } else if (speakerName.toLowerCase().includes('speaker 3')) {
            return 3;
        }
        return 1; // Default to Speaker 1
    }
    
    handleSpeakerChange(event) {
        const select = event.target;
        const newSpeakerNum = parseInt(select.value);
        
        // Update the visual styling
        select.className = `speaker-selector speaker-${newSpeakerNum}`;
        
        // Could add immediate visual feedback here
        console.log(`Caption ${select.dataset.index} reassigned to Speaker ${newSpeakerNum}`);
    }
    
    async backToInput() {
        console.log('🏠 BACK TO INPUT: Clearing state and returning to input');
        
        try {
            // Clear all app state first
            await this.clearAppState();
            
            // Also call the specific back_to_input endpoint if we have a job ID
            if (this.currentJobId) {
                const response = await fetch('/api/back_to_input', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        job_id: this.currentJobId
                    })
                });
                
                const result = await response.json();
                if (!response.ok) {
                    console.warn('Back to input API warning:', result.error);
                }
            }
            
            // Clear current data
            this.currentJobId = null;
            this.currentClipData = null;
            
            // Reset form
            document.getElementById('clipForm').reset();
            
            // Go back to input screen
            this.showScreen(1);
            
            console.log('✅ Successfully returned to input with clean state');
            
        } catch (error) {
            console.error('Back to input error:', error);
            this.showError('Network error occurred');
        }
    }
    
    formatSecondsToMMSS(seconds) {
        const minutes = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${minutes}:${secs.toString().padStart(2, '0')}`;
    }
    
    // 🆕 HYBRID APPROACH METHODS
    
    showLivePreview(updatedCaptions) {
        // Update visual indicators to show this is preview mode
        const videoSection = document.querySelector('.video-section');
        
        // Add preview indicator
        let previewIndicator = videoSection.querySelector('.preview-indicator');
        if (!previewIndicator) {
            previewIndicator = document.createElement('div');
            previewIndicator.className = 'preview-indicator';
            previewIndicator.innerHTML = `
                <div class="preview-badge">
                    🔄 Live Preview - Final video generating...
                </div>
            `;
            videoSection.insertBefore(previewIndicator, videoSection.firstChild);
        }
        
        // Visual feedback for caption changes
        const captionLines = document.querySelectorAll('.caption-line');
        captionLines.forEach((line, index) => {
            line.classList.add('caption-updated');
            setTimeout(() => {
                line.classList.remove('caption-updated');
            }, 2000);
        });
        
        console.log('✨ Live preview activated with', updatedCaptions.length, 'updated captions');
    }
    
    showRegenerationProgress() {
        // Add regeneration progress indicator
        const captionActions = document.querySelector('.caption-actions');
        
        let regenProgress = captionActions.querySelector('.regeneration-progress');
        if (!regenProgress) {
            regenProgress = document.createElement('div');
            regenProgress.className = 'regeneration-progress';
            regenProgress.innerHTML = `
                <div class="regen-status">
                    <div class="regen-spinner">🔄</div>
                    <span class="regen-text">Generating final video...</span>
                    <div class="regen-progress-bar">
                        <div class="regen-progress-fill" style="width: 0%"></div>
                    </div>
                </div>
            `;
            captionActions.appendChild(regenProgress);
        }
    }
    
    handleRegenerationUpdate(data) {
        console.log('Regeneration update:', data);
        
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
        console.log('Regeneration complete:', data);
        
        // Remove progress indicator
        const regenProgress = document.querySelector('.regeneration-progress');
        if (regenProgress) {
            regenProgress.remove();
        }
        
        // Update preview indicator
        const previewIndicator = document.querySelector('.preview-indicator');
        if (previewIndicator) {
            previewIndicator.innerHTML = `
                <div class="preview-badge success">
                    ✅ Final video ready! Use refresh button to see updated version.
                </div>
            `;
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                if (previewIndicator && previewIndicator.parentNode) {
                    previewIndicator.remove();
                }
            }, 5000);
        }
        
        // Show success message with FIXED refresh option
        this.showVideoUpdatedNotificationFixed();
    }
    
    handleRegenerationError(data) {
        console.error('Regeneration error:', data);
        
        // Remove progress indicator
        const regenProgress = document.querySelector('.regeneration-progress');
        if (regenProgress) {
            regenProgress.remove();
        }
        
        // Update preview indicator with error
        const previewIndicator = document.querySelector('.preview-indicator');
        if (previewIndicator) {
            previewIndicator.innerHTML = `
                <div class="preview-badge error">
                    ❌ Video regeneration failed - using preview only
                </div>
            `;
        }
        
        this.showError(`Video regeneration failed: ${data.error}`);
    }
    
    // 🔧 FIX #1: Fixed notification that refreshes video without changing screens
    showVideoUpdatedNotificationFixed() {
        // Create notification with FIXED refresh functionality
        const notification = document.createElement('div');
        notification.className = 'video-updated-notification';
        notification.innerHTML = `
            <div class="notification-content">
                <div class="notification-icon">🎉</div>
                <div class="notification-text">
                    <strong>Video Updated Successfully!</strong><br>
                    Your captions have been applied to the final video.
                </div>
                <button class="notification-refresh-btn" id="smart-refresh-btn">
                    🔄 Refresh Video
                </button>
                <button class="notification-close-btn" onclick="this.parentElement.parentElement.remove()">
                    ×
                </button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Add event listener for SMART refresh that stays on caption screen
        document.getElementById('smart-refresh-btn').addEventListener('click', () => {
            this.refreshVideoInPlace();
            notification.remove();
        });
        
        // Auto-remove after 10 seconds if not manually closed
        setTimeout(() => {
            if (notification && notification.parentNode) {
                notification.remove();
            }
        }, 10000);
    }
    
    // OAuth Methods
    async checkOAuthStatus() {
        try {
            const response = await fetch('/api/oauth/status');
            const result = await response.json();
            this.updateOAuthDisplay(result);
        } catch (error) {
            console.error('OAuth status check failed:', error);
            this.updateOAuthDisplay({
                authenticated: false,
                status: 'error',
                message: 'Failed to check authentication status'
            });
        }
    }
    
    updateOAuthDisplay(oauthStatus) {
        const indicator = document.getElementById('oauth-indicator');
        const message = document.getElementById('oauth-message');
        const authBtn = document.getElementById('authenticate-btn');
        const testBtn = document.getElementById('test-upload-btn');
        const revokeBtn = document.getElementById('revoke-auth-btn');
        const uploadForm = document.getElementById('upload-form-section');
        
        if (oauthStatus.authenticated) {
            indicator.textContent = '✅';
            message.textContent = oauthStatus.message;
            authBtn.style.display = 'none';
            testBtn.style.display = 'inline-block';
            revokeBtn.style.display = 'inline-block';
            uploadForm.style.opacity = '1';
            uploadForm.style.pointerEvents = 'auto';
        } else {
            indicator.textContent = '❌';
            message.textContent = oauthStatus.message;
            authBtn.style.display = 'inline-block';
            testBtn.style.display = 'none';
            revokeBtn.style.display = 'none';
            uploadForm.style.opacity = '0.5';
            uploadForm.style.pointerEvents = 'none';
        }
    }
    
    async authenticateWithYouTube() {
        try {
            const authBtn = document.getElementById('authenticate-btn');
            const originalText = authBtn.innerHTML;
            authBtn.innerHTML = '🔄 Authenticating...';
            authBtn.disabled = true;
            
            const response = await fetch('/api/oauth/authenticate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showSuccess(result.message);
                this.checkOAuthStatus(); // Refresh status
            } else {
                this.showError(result.error || 'Authentication failed');
            }
            
        } catch (error) {
            console.error('Authentication error:', error);
            this.showError('Network error during authentication');
        } finally {
            const authBtn = document.getElementById('authenticate-btn');
            authBtn.innerHTML = '🔑 Authenticate with YouTube';
            authBtn.disabled = false;
        }
    }
    
    async testYouTubeConnection() {
        try {
            const testBtn = document.getElementById('test-upload-btn');
            const originalText = testBtn.innerHTML;
            testBtn.innerHTML = '🔄 Testing...';
            testBtn.disabled = true;
            
            const response = await fetch('/api/test_upload', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showSuccess(`✅ Connection successful!\nChannel: ${result.channel_title}`);
            } else {
                this.showError(`❌ Test failed: ${result.error}`);
            }
            
        } catch (error) {
            console.error('Test error:', error);
            this.showError('Network error during test');
        } finally {
            const testBtn = document.getElementById('test-upload-btn');
            testBtn.innerHTML = '🧪 Test Connection';
            testBtn.disabled = false;
        }
    }
    
    async revokeYouTubeAuth() {
        if (!confirm('Are you sure you want to revoke YouTube access? You\'ll need to re-authenticate to upload videos.')) {
            return;
        }
        
        try {
            const revokeBtn = document.getElementById('revoke-auth-btn');
            const originalText = revokeBtn.innerHTML;
            revokeBtn.innerHTML = '🔄 Revoking...';
            revokeBtn.disabled = true;
            
            const response = await fetch('/api/oauth/revoke', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showSuccess(result.message);
                this.checkOAuthStatus(); // Refresh status
            } else {
                this.showError(result.error || 'Failed to revoke access');
            }
            
        } catch (error) {
            console.error('Revoke error:', error);
            this.showError('Network error during revoke');
        } finally {
            const revokeBtn = document.getElementById('revoke-auth-btn');
            revokeBtn.innerHTML = '🚫 Revoke Access';
            revokeBtn.disabled = false;
        }
    }

    // 🔧 FIX #1: New method to refresh video without changing screens
    async refreshVideoInPlace() {
        if (!this.currentJobId) {
            this.showError('No active job to refresh');
            return;
        }
        
        try {
            console.log('🔄 Refreshing video in place...');
            
            // Call new API endpoint to get refreshed video data
            const response = await fetch(`/api/refresh_video/${this.currentJobId}`);
            const result = await response.json();
            
            if (response.ok) {
                // Update current clip data
                this.currentClipData = result.clip_data;
                
                // Reload video with cache-busting URL
                const video = document.getElementById('clip-video');
                const videoSource = document.getElementById('video-source');
                videoSource.src = result.video_url;  // This includes cache-buster
                video.load();
                
                // Update detection info
                this.displayDetectionInfo(result.clip_data);
                
                // Reload captions if available
                if (result.captions) {
                    this.loadCaptions(result.captions);
                }
                
                // Show success message
                this.showSuccess('✅ Video refreshed successfully with updated captions!');
                
                console.log('✅ Video refreshed in place successfully');
            } else {
                console.error('❌ Failed to refresh video:', result.error);
                this.showError(result.error || 'Failed to refresh video');
            }
        } catch (error) {
            console.error('❌ Refresh video error:', error);
            this.showError('Network error while refreshing video');
        }
    }

    // 🆕 NEW: Clear application state methods
    async clearAppState() {
        try {
            console.log('🧺 CLEARING: Application state reset');
            
            // Clear frontend state
            this.currentJobId = null;
            this.currentClipData = null;
            
            // Clear backend state
            const response = await fetch('/api/clear_all_jobs', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const result = await response.json();
            
            if (response.ok) {
                console.log(`🧺 CLEARED: ${result.jobs_cleared} backend jobs`);
            } else {
                console.warn('⚠️ Failed to clear backend state:', result.error);
            }
            
        } catch (error) {
            console.error('❌ Clear state error:', error);
        }
    }
    
    async getAppState() {
        try {
            const response = await fetch('/api/app_state');
            const result = await response.json();
            
            if (response.ok) {
                console.log('📊 APP STATE:', result);
                return result;
            } else {
                console.error('Failed to get app state:', result.error);
                return null;
            }
        } catch (error) {
            console.error('App state error:', error);
            return null;
        }
    }
    
    addClearStateButton() {
        // Add a debug button to manually clear state (remove in production)
        const header = document.querySelector('.header');
        if (header && !document.getElementById('debug-clear-btn')) {
            const debugBtn = document.createElement('button');
            debugBtn.id = 'debug-clear-btn';
            debugBtn.innerHTML = '🧺 Clear All State (Debug)';
            debugBtn.style.cssText = `
                position: fixed;
                top: 10px;
                right: 10px;
                background: #ff4444;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 12px;
                cursor: pointer;
                z-index: 9999;
                opacity: 0.8;
            `;
            
            debugBtn.addEventListener('click', async () => {
                console.log('🧺 MANUAL CLEAR: Clearing all state manually');
                await this.clearAppState();
                
                // Reset form
                document.getElementById('clipForm').reset();
                
                // Go to input screen
                this.showScreen(1);
                
                alert('🧺 All state cleared! Try entering a new URL now.');
            });
            
            document.body.appendChild(debugBtn);
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.viralClipperApp = new ViralClipperApp();
});

// Utility functions
function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

function formatFileSize(bytes) {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
}
