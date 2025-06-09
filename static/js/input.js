// 🎬 Clippy - Input Page JavaScript

class InputPage {
    constructor() {
        this.form = document.getElementById('clipForm');
        this.durationSlider = document.getElementById('duration-slider');
        this.durationInput = document.getElementById('duration');
        
        this.initializeEventListeners();
        this.loadRecentActivity();
    }

    initializeEventListeners() {
        // Form submission
        if (this.form) {
            this.form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleFormSubmit();
            });
        }

        // Duration slider sync
        if (this.durationSlider && this.durationInput) {
            this.durationSlider.addEventListener('input', (e) => {
                this.durationInput.value = e.target.value;
            });

            this.durationInput.addEventListener('input', (e) => {
                this.durationSlider.value = e.target.value;
            });
        }

        // Check for return from auth
        this.checkForAuthReturn();
    }

    async handleFormSubmit() {
        const formData = new FormData(this.form);
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
            const response = await fetch('/api/generate_clip', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                // Redirect to processing page
                window.location.href = `/process?job_id=${result.job_id}`;
            } else {
                window.clippyBase.showError(result.error || 'Failed to start clip generation');
            }
        } catch (error) {
            console.error('Generate clip error:', error);
            window.clippyBase.showError('Network error occurred');
        }
    }

    validateInputs(data) {
        // URL validation
        if (!data.url || (!data.url.includes('youtube.com') && !data.url.includes('youtu.be'))) {
            window.clippyBase.showError('Please enter a valid YouTube URL');
            return false;
        }

        // Duration validation
        if (data.duration < 10 || data.duration > 60) {
            window.clippyBase.showError('Duration must be between 10 and 60 seconds');
            return false;
        }

        // Time validation
        if (data.start_time && data.end_time) {
            const startSeconds = window.clippyBase.parseTimeToSeconds(data.start_time);
            const endSeconds = window.clippyBase.parseTimeToSeconds(data.end_time);
            
            if (startSeconds === null || endSeconds === null) {
                window.clippyBase.showError('Invalid time format. Use MM:SS or seconds');
                return false;
            }
            
            if (startSeconds >= endSeconds) {
                window.clippyBase.showError('End time must be after start time');
                return false;
            }
        }

        return true;
    }

    async loadRecentActivity() {
        // Only load if user is authenticated
        if (!window.clippyBase.currentUser) {
            return;
        }

        try {
            const response = await fetch('/api/user_activity');
            if (!response.ok) return;

            const result = await response.json();
            
            if (result.recent_clips && result.recent_clips.length > 0) {
                const activitySection = document.getElementById('recent-activity');
                if (activitySection) {
                    let html = '<h3>Recent Clips</h3><div class="recent-clips-grid">';
                    
                    result.recent_clips.slice(0, 6).forEach(clip => {
                        const date = new Date(clip.created_at).toLocaleDateString();
                        const thumbnail = clip.thumbnail || '/static/img/default-thumbnail.png';
                        
                        html += `
                            <div class="recent-clip-card">
                                <div class="clip-thumbnail">
                                    <img src="${thumbnail}" alt="Clip thumbnail">
                                    <div class="clip-duration">${clip.duration}s</div>
                                </div>
                                <div class="clip-info">
                                    <div class="clip-title">${this.truncateText(clip.original_title, 50)}</div>
                                    <div class="clip-date">${date}</div>
                                </div>
                                <div class="clip-actions">
                                    ${clip.job_id ? `
                                        <button class="btn btn-sm btn-ghost" onclick="inputPage.loadClip('${clip.job_id}')">
                                            <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                                            </svg>
                                        </button>
                                    ` : ''}
                                </div>
                            </div>
                        `;
                    });
                    
                    html += '</div>';
                    activitySection.innerHTML = html;
                    activitySection.classList.remove('hidden');
                }
            }
        } catch (error) {
            console.error('Failed to load recent activity:', error);
        }
    }

    loadClip(jobId) {
        // Navigate to edit page with the job ID
        window.location.href = `/edit?job_id=${jobId}`;
    }

    truncateText(text, maxLength) {
        if (!text) return '';
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }

    checkForAuthReturn() {
        // Check if we're returning from authentication
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('auth') === 'success') {
            window.clippyBase.showSuccess('Successfully signed in!');
            
            // Clean up URL
            window.history.replaceState({}, document.title, '/');
            
            // Reload recent activity
            this.loadRecentActivity();
        }
    }
}

// Add CSS for input page specific styles
const inputPageStyles = `
<style>
/* Input Page Specific Styles */
.input-page {
    max-width: 800px;
    margin: 0 auto;
}

.hero-section {
    text-align: center;
    margin-bottom: var(--space-2xl);
}

.hero-title {
    font-size: var(--text-3xl);
    font-weight: 700;
    margin-bottom: var(--space-sm);
    background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-subtitle {
    font-size: var(--text-lg);
    color: var(--color-text-secondary);
}

.main-card {
    margin-bottom: var(--space-2xl);
}

/* Time Input Section */
.time-input-section {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
    border: 2px solid var(--color-primary);
    border-radius: var(--radius-xl);
    padding: var(--space-xl);
    margin-bottom: var(--space-xl);
}

.time-input-header {
    display: flex;
    align-items: center;
    gap: var(--space-sm);
    margin-bottom: var(--space-lg);
}

.time-input-header svg {
    width: 24px;
    height: 24px;
    color: var(--color-primary);
}

.time-input-title {
    font-size: var(--text-lg);
    font-weight: 600;
}

.time-input-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-md);
}

/* Duration Slider */
.duration-slider {
    display: flex;
    align-items: center;
    gap: var(--space-md);
}

.slider {
    flex: 1;
    height: 6px;
    border-radius: 3px;
    background: var(--color-surface-overlay);
    outline: none;
    -webkit-appearance: none;
}

.slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: var(--color-primary);
    cursor: pointer;
    transition: all var(--transition-base);
}

.slider::-webkit-slider-thumb:hover {
    transform: scale(1.2);
    box-shadow: 0 0 10px rgba(99, 102, 241, 0.5);
}

.duration-input {
    width: 80px;
    text-align: center;
}

/* Features Section */
.features-section {
    margin-top: var(--space-3xl);
}

.features-title {
    font-size: var(--text-2xl);
    font-weight: 600;
    text-align: center;
    margin-bottom: var(--space-sm);
}

.features-subtitle {
    text-align: center;
    color: var(--color-text-secondary);
    margin-bottom: var(--space-xl);
}

.features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: var(--space-lg);
}

.feature-card {
    background: var(--color-surface-overlay);
    border-radius: var(--radius-lg);
    padding: var(--space-lg);
    text-align: center;
    transition: all var(--transition-base);
}

.feature-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
}

.feature-icon {
    width: 48px;
    height: 48px;
    margin: 0 auto var(--space-md);
    color: var(--color-primary);
}

.feature-card h4 {
    font-size: var(--text-base);
    font-weight: 600;
    margin-bottom: var(--space-xs);
}

.feature-card p {
    font-size: var(--text-sm);
    color: var(--color-text-secondary);
}

/* Recent Activity */
.recent-activity {
    margin-top: var(--space-3xl);
}

.recent-activity h3 {
    font-size: var(--text-xl);
    font-weight: 600;
    margin-bottom: var(--space-lg);
}

.recent-clips-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: var(--space-md);
}

.recent-clip-card {
    background: var(--color-surface-overlay);
    border-radius: var(--radius-lg);
    padding: var(--space-md);
    display: flex;
    gap: var(--space-md);
    align-items: center;
    transition: all var(--transition-base);
}

.recent-clip-card:hover {
    background: var(--color-surface-elevated);
    transform: translateY(-2px);
}

.clip-thumbnail {
    position: relative;
    width: 80px;
    height: 60px;
    border-radius: var(--radius-md);
    overflow: hidden;
    flex-shrink: 0;
}

.clip-thumbnail img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.clip-duration {
    position: absolute;
    bottom: 4px;
    right: 4px;
    background: rgba(0, 0, 0, 0.8);
    color: white;
    padding: 2px 6px;
    border-radius: var(--radius-sm);
    font-size: var(--text-xs);
}

.clip-info {
    flex: 1;
    min-width: 0;
}

.clip-title {
    font-size: var(--text-sm);
    font-weight: 500;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.clip-date {
    font-size: var(--text-xs);
    color: var(--color-text-muted);
    margin-top: 2px;
}

.clip-actions {
    display: flex;
    gap: var(--space-xs);
}

/* Responsive */
@media (max-width: 768px) {
    .time-input-grid {
        grid-template-columns: 1fr;
    }
    
    .features-grid {
        grid-template-columns: 1fr;
    }
    
    .recent-clips-grid {
        grid-template-columns: 1fr;
    }
}
</style>
`;

// Add styles to document
document.head.insertAdjacentHTML('beforeend', inputPageStyles);

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.inputPage = new InputPage();
});
