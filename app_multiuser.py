#!/usr/bin/env python3
"""
🎯 VIRAL CLIPPER WEB APP - MULTI-USER VERSION 🎯
Flask web application with multi-user OAuth support
"""

# Load environment variables first
from dotenv import load_dotenv
load_dotenv()

# For local development, allow OAuth over HTTP
import os
if os.getenv('FLASK_ENV') == 'development':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect, url_for, g
from flask_socketio import SocketIO, emit
import os
import json
import uuid
import threading
import time
from datetime import datetime

# Import our modules
from auto_peak_viral_clipper import AutoPeakViralClipper
from caption_fragment_fix import merge_fragmented_captions
from ass_caption_update_system_v2 import ASSCaptionUpdateSystemV2 as ASSCaptionUpdateSystem

# Import auth modules
from auth import login_required, get_current_user, OAuthManager, User
from auth.decorators import youtube_service_required, logout_user
from database import init_db

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'viral_clipper_secret_key_2025')
app.config['PERMANENT_SESSION_LIFETIME'] = 604800  # 7 days in seconds

# Database configuration
app.config['DB_HOST'] = os.getenv('DB_HOST', 'localhost')
app.config['DB_PORT'] = os.getenv('DB_PORT', 5432)
app.config['DB_NAME'] = os.getenv('DB_NAME', 'clippy')
app.config['DB_USER'] = os.getenv('DB_USER', 'clippy_user')
app.config['DB_PASSWORD'] = os.getenv('DB_PASSWORD', 'clippy_password')

# Initialize database
init_db(app)

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize the clipper with ASS captions
clipper = AutoPeakViralClipper()

# Initialize OAuth manager
oauth_manager = OAuthManager()

# Store active jobs (now per user)
active_jobs = {}


class ClipJob:
    """Represents a clip generation job"""
    def __init__(self, job_id, user_id, url, duration, start_time=None, end_time=None):
        self.job_id = job_id
        self.user_id = user_id  # Track which user owns this job
        self.url = url
        self.duration = duration
        self.start_time = start_time
        self.end_time = end_time
        self.status = "starting"
        self.progress = 0
        self.message = "Initializing..."
        self.clip_data = None
        self.error = None
        self.created_at = datetime.now()
        self.regeneration_status = None
        self.regeneration_progress = 0
        self.regeneration_job_id = None


def update_job_progress(job_id, status, progress, message):
    """Update job progress and emit to frontend"""
    if job_id in active_jobs:
        job = active_jobs[job_id]
        job.status = status
        job.progress = progress
        job.message = message
        
        # Emit to specific user's room
        socketio.emit('progress_update', {
            'job_id': job_id,
            'status': status,
            'progress': progress,
            'message': message
        }, room=f"user_{job.user_id}")


def process_clip_generation(job_id):
    """Background thread for clip generation"""
    try:
        job = active_jobs[job_id]
        
        update_job_progress(job_id, "processing", 5, "Starting clip generation...")
        
        # Calculate actual start time for processing
        if job.start_time is not None and job.end_time is not None:
            actual_start_time = job.start_time
            actual_duration = job.end_time - job.start_time
            update_job_progress(job_id, "processing", 10, "Using manual time selection...")
        else:
            actual_start_time = None
            actual_duration = job.duration
            update_job_progress(job_id, "processing", 10, "Using auto-detection...")
        
        update_job_progress(job_id, "processing", 20, "Downloading video...")
        
        # Generate the clip
        clip_data = clipper.generate_auto_peak_viral_clip(
            video_url=job.url,
            duration=actual_duration,
            manual_start_time=actual_start_time
        )
        
        if clip_data:
            job.clip_data = clip_data
            update_job_progress(job_id, "completed", 100, "Clip generated successfully!")
            
            # Extract caption data for editing
            caption_data = extract_caption_data(clip_data)
            job.clip_data['captions'] = caption_data
            
            socketio.emit('clip_completed', {
                'job_id': job_id,
                'clip_data': clip_data,
                'captions': caption_data
            }, room=f"user_{job.user_id}")
        else:
            job.error = "Clip generation failed"
            update_job_progress(job_id, "error", 0, "Clip generation failed")
            
    except Exception as e:
        job.error = str(e)
        update_job_progress(job_id, "error", 0, f"Error: {str(e)}")


# Auth routes
@app.route('/api/auth/login')
def auth_login():
    """Initiate OAuth login flow"""
    redirect_uri = url_for('auth_callback', _external=True)
    authorization_url, state = oauth_manager.get_authorization_url(redirect_uri)
    
    # Store state in session for CSRF protection
    session['oauth_state'] = state
    
    return jsonify({
        'authorization_url': authorization_url,
        'status': 'redirect_required'
    })


@app.route('/api/auth/callback')
def auth_callback():
    """Handle OAuth callback"""
    # Verify state
    state = request.args.get('state')
    stored_state = session.pop('oauth_state', None)
    
    if not state or state != stored_state:
        return render_template('auth_error.html', error='Invalid state parameter')
    
    # Handle the callback
    redirect_uri = url_for('auth_callback', _external=True)
    user = oauth_manager.handle_oauth_callback(
        request.url, state, redirect_uri
    )
    
    if user:
        # Redirect to main app
        return redirect(url_for('index'))
    else:
        return render_template('auth_error.html', error='Authentication failed')


@app.route('/api/auth/logout', methods=['POST'])
def auth_logout():
    """Logout user"""
    logout_user()
    return jsonify({'status': 'success', 'message': 'Logged out successfully'})


@app.route('/api/auth/status')
def auth_status():
    """Check authentication status"""
    user = get_current_user()
    
    if user:
        return jsonify({
            'authenticated': True,
            'user': user.to_dict()
        })
    else:
        return jsonify({
            'authenticated': False
        })


# Main routes
@app.route('/')
def index():
    """Main page"""
    return render_template('index_multiuser.html')


@app.route('/api/generate_clip', methods=['POST'])
@login_required
def generate_clip():
    """Start clip generation process"""
    user = get_current_user()
    data = request.json
    
    # Validate input
    url = data.get('url', '').strip()
    if not url or 'youtube.com' not in url and 'youtu.be' not in url:
        return jsonify({'error': 'Invalid YouTube URL'}), 400
    
    duration = data.get('duration', 30)
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    
    # Convert MM:SS to seconds if provided
    if start_time:
        start_time = parse_time_to_seconds(start_time)
    if end_time:
        end_time = parse_time_to_seconds(end_time)
    
    # Create job
    job_id = str(uuid.uuid4())
    job = ClipJob(job_id, user.id, url, duration, start_time, end_time)
    active_jobs[job_id] = job
    
    # Start background processing
    thread = threading.Thread(target=process_clip_generation, args=(job_id,))
    thread.daemon = True
    thread.start()
    
    return jsonify({'job_id': job_id, 'status': 'started'})


@app.route('/api/job_status/<job_id>')
@login_required
def job_status(job_id):
    """Get job status"""
    user = get_current_user()
    
    if job_id not in active_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = active_jobs[job_id]
    
    # Ensure user owns this job
    if job.user_id != user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({
        'job_id': job_id,
        'status': job.status,
        'progress': job.progress,
        'message': job.message,
        'clip_data': job.clip_data,
        'error': job.error
    })


@app.route('/api/upload_to_youtube', methods=['POST'])
@youtube_service_required
def upload_to_youtube():
    """Upload clip to YouTube using user's credentials"""
    user = get_current_user()
    youtube_service = g.youtube_service
    
    data = request.json
    job_id = data.get('job_id')
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    privacy_status = data.get('privacy_status', 'private')
    
    if job_id not in active_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = active_jobs[job_id]
    
    # Ensure user owns this job
    if job.user_id != user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if not job.clip_data:
        return jsonify({'error': 'No clip available for upload'}), 400
    
    if not title:
        return jsonify({'error': 'Title is required'}), 400
    
    try:
        video_path = job.clip_data['path']
        
        if not os.path.exists(video_path):
            return jsonify({'error': 'Video file not found'}), 404
        
        # Upload to YouTube
        from googleapiclient.http import MediaFileUpload
        
        body = {
            'snippet': {
                'title': title[:100],
                'description': f"{description}\n\n#Shorts"[:5000],
                'tags': ['Shorts', 'Viral', 'Clips', 'AI', 'AutoGenerated'],
                'categoryId': '22',
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': False,
            }
        }
        
        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        
        insert_request = youtube_service.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )
        
        response = None
        error = None
        retry = 0
        
        while response is None:
            try:
                status, response = insert_request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    socketio.emit('upload_progress', {
                        'job_id': job_id,
                        'progress': progress
                    }, room=f"user_{user.id}")
                    
            except Exception as e:
                error = e
                if retry < 3:
                    retry += 1
                    time.sleep(2 ** retry)
                else:
                    raise
        
        if response and 'id' in response:
            video_id = response['id']
            video_url = f'https://www.youtube.com/watch?v={video_id}'
            
            # Save upload history
            user.add_upload_history(
                video_id=video_id,
                video_title=title,
                video_url=video_url,
                status='completed'
            )
            
            return jsonify({
                'status': 'success',
                'video_id': video_id,
                'url': video_url,
                'message': f'Successfully uploaded: {title}'
            })
        else:
            return jsonify({
                'error': 'Upload completed but no video ID returned'
            }), 500
            
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500


@app.route('/api/upload_history')
@login_required
def get_upload_history():
    """Get user's upload history"""
    user = get_current_user()
    history = user.get_upload_history(limit=20)
    
    return jsonify({
        'uploads': [
            {
                'video_id': item['video_id'],
                'title': item['video_title'],
                'url': item['video_url'],
                'uploaded_at': item['uploaded_at'].isoformat() if item['uploaded_at'] else None,
                'status': item['upload_status']
            }
            for item in history
        ]
    })


@app.route('/clips/<filename>')
def serve_clip(filename):
    """Serve video clips"""
    return send_from_directory('clips', filename)


# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    user = get_current_user()
    if user:
        # Join user-specific room
        room = f"user_{user.id}"
        socketio.server.enter_room(request.sid, room)
        print(f'User {user.email} connected to room {room}')
    else:
        print('Anonymous client connected')


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    user = get_current_user()
    if user:
        print(f'User {user.email} disconnected')
    else:
        print('Anonymous client disconnected')


# Helper functions
def parse_time_to_seconds(time_str):
    """Convert MM:SS or seconds to seconds"""
    if not time_str:
        return None
    
    time_str = str(time_str).strip()
    
    if ':' in time_str:
        parts = time_str.split(':')
        if len(parts) == 2:
            try:
                minutes = int(parts[0])
                seconds = int(parts[1])
                return minutes * 60 + seconds
            except ValueError:
                return None
    else:
        try:
            return float(time_str)
        except ValueError:
            return None
    
    return None


def extract_caption_data(clip_data):
    """Extract caption data from subtitle files"""
    subtitle_file = clip_data.get('subtitle_file')
    if not subtitle_file or not os.path.exists(subtitle_file):
        return []
    
    if subtitle_file.endswith('.srt'):
        return extract_captions_from_srt_fixed(subtitle_file)
    elif subtitle_file.endswith('.ass'):
        return extract_captions_from_ass_fixed(subtitle_file)
    
    return []


def extract_captions_from_srt_fixed(srt_file_path: str):
    """Extract captions from SRT file"""
    captions = []
    
    try:
        with open(srt_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = content.replace('\\n', '\n')
        subtitle_blocks = content.strip().split('\n\n')
        
        for block in subtitle_blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                try:
                    index = int(lines[0])
                    timing = lines[1]
                    text = '\n'.join(lines[2:])
                    
                    if ' --> ' in timing:
                        start_time_str, end_time_str = timing.split(' --> ')
                        
                        speaker = 'Speaker 1'
                        if text.startswith('[') and '] ' in text:
                            speaker_end = text.find('] ')
                            speaker = text[1:speaker_end]
                            text = text[speaker_end + 2:]
                        
                        captions.append({
                            'text': text.strip(),
                            'speaker': speaker,
                            'start_time': start_time_str.strip(),
                            'end_time': end_time_str.strip(),
                            'index': index
                        })
                        
                except Exception:
                    continue
        
        return captions
        
    except Exception as e:
        print(f"Error reading SRT file: {e}")
        return []


def extract_captions_from_ass_fixed(ass_file_path: str):
    """Extract captions from ASS file"""
    captions = []
    
    try:
        with open(ass_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if line.startswith('Dialogue:'):
                try:
                    parts = line.split(',', 9)
                    if len(parts) >= 10:
                        start_time = parts[1]
                        end_time = parts[2]
                        speaker = parts[3] if parts[3] else 'Speaker 1'
                        text = parts[9]
                        
                        import re
                        text = re.sub(r'{[^}]*}', '', text)
                        text = text.strip()
                        
                        if text:
                            captions.append({
                                'text': text,
                                'speaker': speaker,
                                'start_time': start_time,
                                'end_time': end_time,
                                'index': len(captions)
                            })
                            
                except Exception:
                    continue
        
        return captions
        
    except Exception as e:
        print(f"Error reading ASS file: {e}")
        return []


@app.route('/api/update_captions', methods=['POST'])
@login_required
def update_captions():
    """Update captions with edited text and speaker assignments"""
    user = get_current_user()
    data = request.json
    job_id = data.get('job_id')
    captions = data.get('captions', [])
    
    if job_id not in active_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = active_jobs[job_id]
    
    # Ensure user owns this job
    if job.user_id != user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if not job.clip_data:
        return jsonify({'error': 'No clip data available'}), 400
    
    try:
        # Preprocess captions to fix fragmentation
        avg_text_length = sum(len(c.get('text', '')) for c in captions) / len(captions) if captions else 0
        
        if avg_text_length < 5:
            captions = merge_fragmented_captions(captions)
        
        # Start background regeneration
        regeneration_thread = threading.Thread(
            target=regenerate_video_background_ass, 
            args=(job_id, captions)
        )
        regeneration_thread.daemon = True
        regeneration_thread.start()
        
        return jsonify({
            'status': 'success', 
            'message': 'Caption update started. Video is being regenerated in background.',
            'regeneration_started': True
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to start caption update: {str(e)}'}), 500


def regenerate_video_background_ass(job_id, updated_captions):
    """Background thread for video regeneration using ASS caption system"""
    try:
        job = active_jobs[job_id]
        original_clip_data = job.clip_data
        
        job.regeneration_status = 'processing'
        job.regeneration_progress = 10
        
        socketio.emit('regeneration_update', {
            'job_id': job_id,
            'status': 'processing',
            'progress': 10,
            'message': 'Creating captions using ASS system...'
        }, room=f"user_{job.user_id}")
        
        subtitle_file = original_clip_data.get('subtitle_file')
        original_video_path = original_clip_data['path']
        
        if not subtitle_file:
            raise Exception('Caption file not found')
        
        job.regeneration_progress = 30
        socketio.emit('regeneration_update', {
            'job_id': job_id,
            'status': 'processing',
            'progress': 30,
            'message': 'Using ASS caption system...'
        }, room=f"user_{job.user_id}")
        
        success = clipper.update_captions_ass(subtitle_file, updated_captions)
        
        if not success:
            raise Exception('Failed to update captions using ASS system')
        
        job.regeneration_progress = 50
        socketio.emit('regeneration_update', {
            'job_id': job_id,
            'status': 'processing',
            'progress': 50,
            'message': 'Creating video with updated captions...'
        }, room=f"user_{job.user_id}")
        
        temp_ass_path = original_video_path.replace('.mp4', '_ASS_temp.mp4')
        base_video_path = original_video_path.replace('.mp4', '_temp_switching.mp4')
        
        if not os.path.exists(base_video_path):
            no_caption_path = original_video_path.replace('.mp4', '_no_captions.mp4')
            if os.path.exists(no_caption_path):
                base_video_path = no_caption_path
            else:
                base_video_path = original_video_path
        
        job.regeneration_progress = 70
        socketio.emit('regeneration_update', {
            'job_id': job_id,
            'status': 'processing',
            'progress': 70,
            'message': 'Burning ASS captions into video...'
        }, room=f"user_{job.user_id}")
        
        success = clipper.burn_captions_into_video_debug(
            base_video_path,
            subtitle_file,
            temp_ass_path
        )
        
        if not success:
            raise Exception('Failed to burn ASS captions into video')
        
        job.regeneration_progress = 90
        socketio.emit('regeneration_update', {
            'job_id': job_id,
            'status': 'processing',
            'progress': 90,
            'message': 'Finalizing ASS caption video...'
        }, room=f"user_{job.user_id}")
        
        if os.path.exists(original_video_path):
            os.remove(original_video_path)
        
        os.rename(temp_ass_path, original_video_path)
        
        job.clip_data['updated_at'] = datetime.now().isoformat()
        job.clip_data['caption_updates'] = len(updated_captions)
        job.clip_data['ass_captions_applied'] = True
        
        job.regeneration_status = 'completed'
        job.regeneration_progress = 100
        
        socketio.emit('regeneration_complete', {
            'job_id': job_id,
            'status': 'completed',
            'progress': 100,
            'message': 'Video updated with captions!',
            'updated_path': original_video_path
        }, room=f"user_{job.user_id}")
        
    except Exception as e:
        print(f"Video regeneration failed for job {job_id}: {e}")
        
        if job_id in active_jobs:
            job = active_jobs[job_id]
            job.regeneration_status = 'failed'
            job.regeneration_progress = 0
            
            socketio.emit('regeneration_error', {
                'job_id': job_id,
                'status': 'failed',
                'error': f'ASS regeneration failed: {str(e)}'
            }, room=f"user_{job.user_id}")


@app.route('/api/refresh_video/<job_id>')
@login_required
def refresh_video(job_id):
    """Refresh video data without changing screens"""
    user = get_current_user()
    
    if job_id not in active_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = active_jobs[job_id]
    
    # Ensure user owns this job
    if job.user_id != user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if not job.clip_data:
        return jsonify({'error': 'No clip data available'}), 400
    
    caption_data = extract_caption_data(job.clip_data)
    job.clip_data['captions'] = caption_data
    
    video_path = job.clip_data['path']
    filename = os.path.basename(video_path)
    cache_buster = str(int(time.time()))
    
    return jsonify({
        'status': 'success',
        'clip_data': job.clip_data,
        'captions': caption_data,
        'video_url': f"/clips/{filename}?v={cache_buster}",
        'message': 'Video data refreshed successfully'
    })


@app.route('/api/regeneration_status/<job_id>')
@login_required
def regeneration_status(job_id):
    """Get regeneration status for a job"""
    user = get_current_user()
    
    if job_id not in active_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = active_jobs[job_id]
    
    # Ensure user owns this job
    if job.user_id != user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({
        'job_id': job_id,
        'regeneration_status': job.regeneration_status,
        'regeneration_progress': job.regeneration_progress,
        'video_path': job.clip_data['path'] if job.clip_data else None
    })


@app.route('/api/back_to_input', methods=['POST'])
@login_required
def back_to_input():
    """Go back to input screen and clear current job"""
    user = get_current_user()
    data = request.json
    job_id = data.get('job_id')
    
    if job_id in active_jobs:
        job = active_jobs[job_id]
        # Ensure user owns this job before deleting
        if job.user_id == user.id:
            del active_jobs[job_id]
    
    return jsonify({'status': 'success', 'message': 'Returned to input screen'})


@app.route('/api/clear_all_jobs', methods=['POST'])
@login_required
def clear_all_jobs():
    """Clear all active jobs for current user"""
    user = get_current_user()
    
    try:
        # Clear only jobs belonging to current user
        user_jobs = [job_id for job_id, job in active_jobs.items() if job.user_id == user.id]
        for job_id in user_jobs:
            del active_jobs[job_id]
        
        return jsonify({
            'status': 'success', 
            'message': f'Cleared {len(user_jobs)} active jobs',
            'jobs_cleared': len(user_jobs)
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to clear jobs: {str(e)}'}), 500


@app.route('/api/app_state')
@login_required
def get_app_state():
    """Get current application state for debugging"""
    user = get_current_user()
    
    try:
        # Only show jobs for current user
        user_jobs = {
            job_id: {
                'url': job.url,
                'status': job.status,
                'created_at': job.created_at.isoformat()
            }
            for job_id, job in active_jobs.items() 
            if job.user_id == user.id
        }
        
        state = {
            'user': user.to_dict(),
            'active_jobs_count': len(user_jobs),
            'active_jobs': user_jobs
        }
        
        return jsonify(state)
        
    except Exception as e:
        return jsonify({'error': f'Failed to get app state: {str(e)}'}), 500


if __name__ == '__main__':
    # Ensure required directories exist
    os.makedirs('clips', exist_ok=True)
    os.makedirs('downloads', exist_ok=True)
    
    # Check if database is properly configured
    if not os.getenv('DB_PASSWORD'):
        print("⚠️  WARNING: DB_PASSWORD not set in environment variables")
        print("   Check your .env file")
    
    # Check for encryption key
    if not os.getenv('TOKEN_ENCRYPTION_KEY'):
        print("⚠️  WARNING: TOKEN_ENCRYPTION_KEY not set in environment variables")
        print("   A temporary key will be generated, but this should be set in production")
        print("   Check your .env file")
    
    # Run the app
    print("🎯 Starting Multi-User Viral Clipper Web App...")
    print("🌐 Access at: http://localhost:5000")
    print("🔐 Multi-user authentication: ENABLED")
    print("📤 YouTube upload: Per-user OAuth")
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
