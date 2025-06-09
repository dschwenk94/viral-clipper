// 🎬 Clippy - Base JavaScript
// Shared functionality across all pages

class ClippyBase {
    constructor() {
        this.currentUser = null;
        this.sessionId = null;
        this.initializeBase();
    }

    async initializeBase() {
        // Check authentication status
        await this.checkAuthStatus();
        
        // Initialize error modal close button
        const closeErrorBtn = document.getElementById('close-error-btn');
        if (closeErrorBtn) {
            closeErrorBtn.addEventListener('click', () => {
                document.getElementById('error-modal').classList.add('hidden');
            });
        }
    }

    async checkAuthStatus() {
        try {
            const response = await fetch('/api/auth/status');
            const result = await response.json();
            
            this.currentUser = result.authenticated ? result.user : null;
            this.sessionId = result.session_id;
            
            this.updateAuthUI();
            
        } catch (error) {
            console.error('Auth check failed:', error);
            this.currentUser = null;
            this.updateAuthUI();
        }
    }

    updateAuthUI() {
        const userInfo = document.getElementById('user-info');
        if (!userInfo) return;
        
        if (this.currentUser) {
            // User is authenticated
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
            
        } else {
            // User is not authenticated
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

    async signInWithGoogle() {
        try {
            const response = await fetch('/api/auth/login');
            const result = await response.json();
            
            if (result.authorization_url) {
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
                
                // Redirect to home page
                setTimeout(() => {
                    window.location.href = '/';
                }, 1000);
            }
            
        } catch (error) {
            console.error('Logout error:', error);
            this.showError('Logout failed');
        }
    }

    showError(message) {
        const errorMessage = document.getElementById('error-message');
        const errorModal = document.getElementById('error-modal');
        
        if (errorMessage && errorModal) {
            errorMessage.textContent = message;
            errorModal.classList.remove('hidden');
        }
    }

    showSuccess(message) {
        const notification = document.createElement('div');
        notification.className = 'success-notification';
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    // Utility function to get URL parameters
    getUrlParam(param) {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get(param);
    }

    // Utility function to format seconds to MM:SS
    formatSecondsToMMSS(seconds) {
        const minutes = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${minutes}:${secs.toString().padStart(2, '0')}`;
    }

    // Utility function to parse time to seconds
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
}

// Initialize base functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.clippyBase = new ClippyBase();
});
