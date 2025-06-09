// Upload Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const authRequired = document.getElementById('auth-required');
    const uploadInterface = document.getElementById('upload-interface');
    const platformTabs = document.querySelectorAll('.platform-tab');
    const platformUploadForm = document.getElementById('platform-upload-form');
    const signinBtn = document.getElementById('signin-btn');
    const jobId = document.getElementById('job-id').value;
    
    // Socket.io connection
    const socket = io();
    
    // Check authentication status
    checkAuthStatus();
    
    // Platform tab switching
    platformTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            platformTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            const platform = tab.dataset.platform;
            loadPlatformForm(platform);
        });
    });
    
    // Sign in button handler
    if (signinBtn) {
        signinBtn.addEventListener('click', () => {
            // Initiate OAuth login
                fetch('/api/auth/login')
                    .then(response => response.json())
                    .then(data => {
                        if (data.authorization_url) {
                            window.location.href = data.authorization_url;
                        }
                    })
                    .catch(error => {
                        console.error('Login error:', error);
                        alert('Failed to initiate login');
                    });
        });
    }
    
    // Check authentication status
    async function checkAuthStatus() {
        try {
            const response = await fetch('/api/auth/status');
            const data = await response.json();
            
            if (data.authenticated) {
                authRequired.classList.add('hidden');
                uploadInterface.classList.remove('hidden');
                loadPlatformForm('youtube'); // Default to YouTube
                loadUploadHistory();
                checkTikTokConnection();
            } else {
                authRequired.classList.remove('hidden');
                uploadInterface.classList.add('hidden');
            }
        } catch (error) {
            console.error('Error checking auth status:', error);
            authRequired.classList.remove('hidden');
            uploadInterface.classList.add('hidden');
        }
    }
    
    // Check TikTok connection status
    async function checkTikTokConnection() {
        try {
            const response = await fetch('/api/tiktok/status');
            const data = await response.json();
            
            const tiktokTab = document.getElementById('tiktok-tab');
            if (!data.connected) {
                tiktokTab.classList.add('disabled');
                tiktokTab.setAttribute('title', 'Connect TikTok account first');
            } else {
                tiktokTab.classList.remove('disabled');
                tiktokTab.removeAttribute('title');
            }
        } catch (error) {
            console.error('Error checking TikTok status:', error);
        }
    }
    
    // Load platform-specific upload form
    function loadPlatformForm(platform) {
        if (platform === 'youtube') {
            platformUploadForm.innerHTML = `
                <div class="upload-form youtube-form">
                    <h3>Upload to YouTube</h3>
                    <form id="youtube-upload-form">
                        <div class="form-group">
                            <label for="title">Video Title *</label>
                            <input type="text" id="title" name="title" class="form-control" required 
                                   placeholder="Enter an engaging title for your video">
                        </div>
                        
                        <div class="form-group">
                            <label for="description">Description</label>
                            <textarea id="description" name="description" class="form-control" rows="4"
                                      placeholder="Add a description for your video"></textarea>
                        </div>
                        
                        <div class="form-group">
                            <label for="tags">Tags</label>
                            <input type="text" id="tags" name="tags" class="form-control"
                                   placeholder="Comma-separated tags (e.g., funny, viral, clips)">
                        </div>
                        
                        <div class="form-group">
                            <label for="privacy">Privacy</label>
                            <select id="privacy" name="privacy" class="form-control">
                                <option value="private">Private</option>
                                <option value="unlisted">Unlisted</option>
                                <option value="public">Public</option>
                            </select>
                        </div>
                        
                        <div class="form-actions">
                            <button type="submit" class="btn btn-primary">
                                <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                                </svg>
                                Upload to YouTube
                            </button>
                        </div>
                    </form>
                </div>
            `;
            
            // Attach YouTube form handler
            const youtubeForm = document.getElementById('youtube-upload-form');
            youtubeForm.addEventListener('submit', handleYouTubeUpload);
            
        } else if (platform === 'tiktok') {
            platformUploadForm.innerHTML = `
                <div class="upload-form tiktok-form">
                    <h3>Upload to TikTok</h3>
                    <form id="tiktok-upload-form">
                        <div class="form-group">
                            <label for="caption">Caption *</label>
                            <textarea id="caption" name="caption" class="form-control" rows="3" required
                                      placeholder="Write an engaging caption for your TikTok"></textarea>
                        </div>
                        
                        <div class="form-group">
                            <label for="hashtags">Hashtags</label>
                            <input type="text" id="hashtags" name="hashtags" class="form-control"
                                   placeholder="#fyp #viral #funny">
                        </div>
                        
                        <div class="form-group">
                            <label for="privacy_level">Privacy</label>
                            <select id="privacy_level" name="privacy_level" class="form-control">
                                <option value="SELF_ONLY">Private</option>
                                <option value="MUTUAL_FOLLOW_FRIENDS">Friends</option>
                                <option value="PUBLIC_TO_EVERYONE">Public</option>
                            </select>
                        </div>
                        
                        <div class="form-actions">
                            <button type="submit" class="btn btn-primary">
                                <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                                </svg>
                                Upload to TikTok
                            </button>
                        </div>
                    </form>
                </div>
            `;
            
            // Attach TikTok form handler
            const tiktokForm = document.getElementById('tiktok-upload-form');
            tiktokForm.addEventListener('submit', handleTikTokUpload);
        }
    }
    
    // Handle YouTube upload
    async function handleYouTubeUpload(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const uploadData = {
            job_id: jobId,
            title: formData.get('title'),
            description: formData.get('description'),
            privacy_status: formData.get('privacy')
        };
        
        const submitBtn = e.target.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner"></span> Uploading...';
        
        try {
            const response = await fetch('/api/upload_to_youtube', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(uploadData)
            });
            
            const result = await response.json();
            
            if (response.ok && result.status === 'success') {
                showNotification('Video uploaded successfully!', 'success');
                if (result.url) {
                    window.open(result.url, '_blank');
                }
                loadUploadHistory();
            } else {
                showNotification(result.error || 'Upload failed', 'error');
            }
        } catch (error) {
            console.error('Upload error:', error);
            let errorMessage = 'Upload failed';
            if (error.message.includes('JSON')) {
                errorMessage = 'Server error - please check if you are logged in';
            } else {
                errorMessage = 'Upload failed: ' + error.message;
            }
            showNotification(errorMessage, 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        }
    }
    
    // Handle TikTok upload
    async function handleTikTokUpload(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const uploadData = {
            job_id: jobId,
            title: formData.get('caption'),  // TikTok uses 'title' in backend
            description: formData.get('hashtags'),  // Hashtags go in description
            privacy_level: formData.get('privacy_level'),
            allow_comments: true,
            allow_duet: true,
            allow_stitch: true,
            upload_mode: 'direct'
        };
        
        const submitBtn = e.target.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner"></span> Uploading...';
        
        try {
            const response = await fetch('/api/upload_to_tiktok', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(uploadData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                showNotification('Video uploaded to TikTok successfully!', 'success');
                loadUploadHistory();
            } else {
                showNotification(result.error || 'Upload failed', 'error');
            }
        } catch (error) {
            console.error('Upload error:', error);
            showNotification('Upload failed: ' + error.message, 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        }
    }
    
    // Load upload history
    async function loadUploadHistory() {
        try {
            const response = await fetch('/api/upload_history');
            const data = await response.json();
            const uploads = data.uploads || [];
            
            const historyContainer = document.getElementById('upload-history');
            
            if (uploads.length === 0) {
                historyContainer.innerHTML = '<p class="no-uploads">No uploads yet</p>';
                return;
            }
            
            historyContainer.innerHTML = uploads.map(upload => `
                <div class="upload-history-item">
                    <div class="upload-thumbnail">
                        ${upload.thumbnail ? 
                            `<img src="${upload.thumbnail}" alt="${upload.title}">` :
                            `<div class="no-thumbnail">
                                <svg width="48" height="48" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                                </svg>
                            </div>`
                        }
                    </div>
                    <div class="upload-info">
                        <h4>${upload.title}</h4>
                        <div class="upload-meta">
                            <span class="upload-platform ${upload.platform}">${upload.platform}</span>
                            <span class="upload-date">${formatDate(upload.uploaded_at)}</span>
                        </div>
                        ${upload.url ? 
                            `<a href="${upload.url}" target="_blank" class="view-link">View →</a>` : 
                            ''
                        }
                    </div>
                </div>
            `).join('');
        } catch (error) {
            console.error('Error loading upload history:', error);
        }
    }
    
    // Show notification
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    }
    
    // Format date
    function formatDate(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diff = now - date;
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        
        if (days === 0) {
            return 'Today';
        } else if (days === 1) {
            return 'Yesterday';
        } else if (days < 7) {
            return `${days} days ago`;
        } else {
            return date.toLocaleDateString();
        }
    }
    
    // Socket event handlers
    socket.on('connect', () => {
        console.log('Connected to upload socket');
    });
    
    socket.on('upload_progress', (data) => {
        if (data.job_id === jobId) {
            console.log('Upload progress:', data);
            // Handle upload progress updates
        }
    });
});
