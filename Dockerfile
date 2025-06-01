FROM python:3.11-slim-bullseye

# Install system dependencies for video/audio processing and OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    libsm6 \
    libxext6 \
    libfontconfig1 \
    libxrender1 \
    libglib2.0-0 \
    libgomp1 \
    git \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Create directories for clips and temporary files
RUN mkdir -p clips temp uploads

# Copy and install Python dependencies
COPY requirements_webapp.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements_webapp.txt

# Install production extras
RUN pip install --no-cache-dir gunicorn psutil

# Preload Whisper model for faster startup
RUN python -c "import whisper; whisper.load_model('base')"

# Copy application code
COPY . .

# Create non-root user for security
RUN adduser --disabled-password --gecos '' clippy && \
    chown -R clippy:clippy /app
USER clippy

# Expose Flask port and set environment
EXPOSE 5000
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Command to run the Flask app using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]