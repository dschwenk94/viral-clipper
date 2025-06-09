// 🎬 Clippy - Process Page JavaScript

class ProcessPage {
    constructor() {
        this.jobId = document.getElementById('job-id').value;
        this.socket = null;
        this.progressCircle = document.getElementById('progress-circle');
        this.progressPercentage = document.getElementById('progress-percentage');
        this.progressMessage = document.getElementById('progress-message');
        
        if (!this.jobId) {
            window.location.href = '/';
            return;
        }
        
        this.initializeSocket();
        this.checkJobStatus();
    }

    initializeSocket() {
        // Connect with job_id as query parameter
        this.socket = io({
            query: {
                job_id: this.jobId
            }
        });

        // Socket event listeners
        this.socket.on('connect', () => {
            console.log('Connected to server');
        });

        this.socket.on('connected', (data) => {
            console.log('Joined room:', data.room);
        });

        this.socket.on('progress_update', (data) => {
            if (data.job_id === this.jobId) {
                this.updateProgress(data);
            }
        });

        this.socket.on('clip_completed', (data) => {
            if (data.job_id === this.jobId) {
                this.handleClipCompleted(data);
            }
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from server');
        });
    }

    async checkJobStatus() {
        try {
            const response = await fetch(`/api/job_status/${this.jobId}`);
            if (!response.ok) {
                throw new Error('Job not found');
            }

            const job = await response.json();
            
            if (job.status === 'completed') {
                // Job already completed, redirect to edit
                window.location.href = `/edit?job_id=${this.jobId}`;
            } else if (job.status === 'error') {
                this.showError(job.error || 'Processing failed');
            } else {
                // Update UI with current progress
                this.updateProgress({
                    progress: job.progress || 0,
                    message: job.message || 'Processing...'
                });
            }
        } catch (error) {
            console.error('Job status check error:', error);
            this.showError('Failed to load job status');
        }
    }

    updateProgress(data) {
        // Update circular progress
        const circumference = 2 * Math.PI * 90; // radius = 90
        const offset = circumference - (data.progress / 100) * circumference;
        this.progressCircle.style.strokeDashoffset = offset;

        // Update text
        this.progressPercentage.textContent = `${data.progress}%`;
        this.progressMessage.textContent = data.message;

        // Update steps
        this.updateProgressSteps(data.progress, data.message);

        // Handle error state
        if (data.status === 'error') {
            this.showError(data.message);
        }
    }

    updateProgressSteps(progress, message) {
        const steps = {
            'download': document.getElementById('step-download'),
            'analyze': document.getElementById('step-analyze'),
            'speakers': document.getElementById('step-speakers'),
            'captions': document.getElementById('step-captions'),
            'video': document.getElementById('step-video')
        };

        // Reset all steps
        Object.values(steps).forEach(step => {
            if (step) {
                step.classList.remove('active', 'completed');
            }
        });

        // Activate steps based on progress
        if (progress >= 10) {
            steps.download?.classList.add('active');
        }
        if (progress >= 30) {
            steps.download?.classList.remove('active');
            steps.download?.classList.add('completed');
            steps.analyze?.classList.add('active');
        }
        if (progress >= 50) {
            steps.analyze?.classList.remove('active');
            steps.analyze?.classList.add('completed');
            steps.speakers?.classList.add('active');
        }
        if (progress >= 70) {
            steps.speakers?.classList.remove('active');
            steps.speakers?.classList.add('completed');
            steps.captions?.classList.add('active');
        }
        if (progress >= 90) {
            steps.captions?.classList.remove('active');
            steps.captions?.classList.add('completed');
            steps.video?.classList.add('active');
        }
        if (progress >= 100) {
            steps.video?.classList.remove('active');
            steps.video?.classList.add('completed');
        }
    }

    handleClipCompleted(data) {
        // Show completion state briefly
        this.updateProgress({
            progress: 100,
            message: 'Clip generated successfully!'
        });

        // Redirect to edit page after a short delay
        setTimeout(() => {
            window.location.href = `/edit?job_id=${this.jobId}`;
        }, 1500);
    }

    showError(message) {
        // Hide progress elements
        document.querySelector('.progress-container').style.display = 'none';
        
        // Show error state
        const errorState = document.getElementById('error-state');
        const errorDetails = document.getElementById('error-details');
        
        if (errorState && errorDetails) {
            errorDetails.textContent = message;
            errorState.classList.remove('hidden');
        }
    }
}

// Add process page specific styles
const processPageStyles = `
<style>
/* Process Page Specific Styles */
.process-page {
    min-height: calc(100vh - 200px);
    display: flex;
    align-items: center;
    justify-content: center;
}

.progress-container {
    max-width: 600px;
    width: 100%;
    text-align: center;
}

.progress-header {
    margin-bottom: var(--space-2xl);
}

.progress-title {
    font-size: var(--text-2xl);
    font-weight: 700;
    margin-bottom: var(--space-sm);
}

.progress-subtitle {
    font-size: var(--text-lg);
    color: var(--color-text-secondary);
}

/* Circular Progress */
.circular-progress {
    width: 200px;
    height: 200px;
    margin: 0 auto var(--space-xl);
    position: relative;
}

.circular-progress svg {
    width: 100%;
    height: 100%;
    transform: rotate(-90deg);
}

.progress-bg {
    fill: none;
    stroke: var(--color-surface-overlay);
    stroke-width: 8;
}

.progress-fill {
    fill: none;
    stroke: url(#progressGradient);
    stroke-width: 8;
    stroke-linecap: round;
    transition: stroke-dashoffset var(--transition-slow);
}

.progress-text {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: var(--text-3xl);
    font-weight: 700;
}

.progress-message {
    font-size: var(--text-base);
    color: var(--color-text-secondary);
    margin-bottom: var(--space-xl);
    min-height: 24px;
}

/* Progress Steps */
.progress-steps {
    display: flex;
    flex-direction: column;
    gap: var(--space-md);
    text-align: left;
    max-width: 400px;
    margin: 0 auto;
}

.progress-step {
    display: flex;
    align-items: center;
    gap: var(--space-md);
    padding: var(--space-md);
    background: var(--color-surface-overlay);
    border-radius: var(--radius-lg);
    transition: all var(--transition-base);
}

.step-icon {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--color-surface);
    color: var(--color-text-muted);
    transition: all var(--transition-base);
}

.progress-step.active .step-icon {
    background: var(--color-primary);
    color: white;
    animation: pulse 2s infinite;
}

.progress-step.completed .step-icon {
    background: var(--color-success);
    color: white;
}

.step-content {
    flex: 1;
}

.step-title {
    font-weight: 500;
    font-size: var(--text-base);
}

.step-description {
    font-size: var(--text-sm);
    color: var(--color-text-muted);
}

/* Error State */
.error-state {
    text-align: center;
    padding: var(--space-2xl);
}

.error-icon {
    margin-bottom: var(--space-lg);
}

.error-icon svg {
    width: 64px;
    height: 64px;
    color: var(--color-error);
}

.error-state h3 {
    font-size: var(--text-xl);
    font-weight: 600;
    margin-bottom: var(--space-sm);
}

.error-state p {
    color: var(--color-text-secondary);
    margin-bottom: var(--space-xl);
}

/* Responsive */
@media (max-width: 768px) {
    .circular-progress {
        width: 160px;
        height: 160px;
    }
    
    .progress-text {
        font-size: var(--text-2xl);
    }
}
</style>
`;

// Add styles to document
document.head.insertAdjacentHTML('beforeend', processPageStyles);

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.processPage = new ProcessPage();
});
