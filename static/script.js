// 🎯 Viral Clipper JavaScript - Basic Frontend Logic

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

        return true;
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
        console.log('Clip generation completed:', data);
        // For now, just show success message
        alert('Clip generated successfully!');
        this.showScreen(1);
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
        }
    }

    showError(message) {
        document.getElementById('error-message').textContent = message;
        document.getElementById('error-modal').classList.remove('hidden');
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