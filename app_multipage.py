"""
Clippy - Multi-User Multi-Page Application
Supports anonymous clip generation with optional authentication
"""

import os
import json
import secrets
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.middleware.proxy_fix import ProxyFix
import logging
from pathlib import Path
import shutil

# Import auth modules
from auth.models import init_auth_db, User
from auth.oauth_manager import OAuthManager
from auth.decorators import auth_optional, auth_required

# Import clipper modules
from auto_peak_viral_clipper_srt import process_youtube_video
from srt_viral_caption_system import update_captions_for_job
from storage_optimizer import StorageOptimizer

# Import database connection
from database.connection import get_db_connection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', secrets.token_urlsafe(32))
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

# Configure for proxy (if behind nginx/reverse proxy)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

# Initialize OAuth manager
oauth_manager = OAuthManager(app)

# Initialize storage optimizer
storage_optimizer = StorageOptimizer(
    clips_dir='clips',
    downloads_dir='downloads',
    max_age_days=7,
    max_size_gb=50
)

# Ensure required directories exist
os.makedirs('clips', exist_ok=True)
os.makedirs('downloads', exist_ok=True)
os.makedirs('configs', exist_ok=True)

# Initialize databases
init_auth_db()

# Job storage (in production, use Redis or database)
active_jobs = {}

# ==================== ROUTES ====================

# --- Page Routes ---

@app.route('/')
def index():
    """Home page - Input form"""
    return render_template('pages/input.html')

@app.route('/process')
def process_page():
    """Processing page - Shows progress"""
    job_id = request.args.get('job_id')
    if not job_id:
        return redirect(url_for('index'))
    return render_template('pages/process.html', job_id=job_id)

@app.route('/edit')
@auth_optional
def edit_page(user):
    """Edit captions page"""
    job_id = request.args.get('job_id')
    if not job_id:
        return redirect(url_for('index'))
    
    # Get clip data
    clip_data = get_clip_data(job_id, user)
    if not clip_data:
        return redirect(url_for('index'))
    
    return render_template('pages/edit.html', 
                         job_id=job_id, 
                         clip_data=json.dumps(clip_data))

@app.route('/upload')
@auth_required
def upload_page(user):
    """Upload page - Requires authentication"""
    job_id = request.args.get('job_id')
    if not job_id:
        return redirect(url_for('index'))
    
    # Verify user owns this clip
    clip_data = get_clip_data(job_id, user)
    if not clip_data:
        return redirect(url_for('index'))
    
    return render_template('pages/upload.html', job_id=job_id)

# --- API Routes ---

@app.route('/api/auth/status')
def auth_status():
    """Check authentication status"""
    user = User.get_from_session(session)
    
    return jsonify({
        'authenticated': user is not None,
        'user': user.to_dict() if user else None,
        'session_id': session.get('session_id', str(session.sid) if hasattr(session, 'sid') else None),
        'anonymous_clips_count': get_anonymous_clips_count(session)
    })

@app.route('/api/auth/login')
def auth_login():
    """Initiate OAuth login"""
    provider = request.args.get('provider', 'google')
    try:
        auth_url = oauth_manager.get_authorization_url(provider)
        return jsonify({'authorization_url': auth_url})
    except Exception as e:
        logger.error(f"Auth initiation error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/callback/<provider>')
def auth_callback(provider):
    """Handle OAuth callback"""
    try:
        user_info = oauth_manager.handle_callback(provider)
        
        # Create or update user
        user = User.create_or_update(
            provider=provider,
            provider_id=user_info['id'],
            email=user_info.get('email'),
            name=user_info.get('name'),
            picture_url=user_info.get('picture')
        )
        
        # Store in session
        user.store_in_session(session)
        session.permanent = True
        
        # Convert anonymous clips to user clips
        convert_anonymous_clips(session, user.id)
        
        # Redirect to home with success indicator
        return redirect(url_for('index', auth='success'))
        
    except Exception as e:
        logger.error(f"Auth callback error: {e}")
        return redirect(url_for('index', error='auth_failed'))

@app.route('/api/auth/logout', methods=['POST'])
@auth_required
def auth_logout(user):
    """Logout user"""
    User.clear_session(session)
    return jsonify({'success': True})

@app.route('/api/generate_clip', methods=['POST'])
@auth_optional
def generate_clip(user):
    """Generate a clip from YouTube video"""
    try:
        data = request.json
        url = data.get('url')
        duration = data.get('duration', 30)
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        
        # Validate inputs
        if not url:
            return jsonify({'error': 'YouTube URL is required'}), 400
        
        # Create job
        job_id = f"job_{secrets.token_urlsafe(16)}"
        user_id = user.id if user else None
        session_id = session.get('session_id', str(session.sid) if hasattr(session, 'sid') else None)
        
        # Store job info
        active_jobs[job_id] = {
            'status': 'pending',
            'progress': 0,
            'user_id': user_id,
            'session_id': session_id,
            'url': url,
            'created_at': datetime.now().isoformat()
        }
        
        # Process in background
        socketio.start_background_task(
            process_video_task,
            job_id, url, duration, start_time, end_time, 
            user_id, session_id
        )
        
        return jsonify({
            'job_id': job_id,
            'is_anonymous': user_id is None
        })
        
    except Exception as e:
        logger.error(f"Generate clip error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/job_status/<job_id>')
@auth_optional
def job_status(job_id, user):
    """Get job status"""
    job = active_jobs.get(job_id)
    if not job:
        # Check database
        job = get_job_from_db(job_id, user)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
    
    # Verify access
    if not can_access_job(job, user, session):
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify(job)

@app.route('/api/user_activity')
@auth_required
def user_activity(user):
    """Get user's recent activity"""
    try:
        clips = get_user_clips(user.id, limit=10)
        return jsonify({
            'recent_clips': clips
        })
    except Exception as e:
        logger.error(f"User activity error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/update_captions', methods=['POST'])
@auth_optional
def update_captions_api(user):
    """Update captions for a clip"""
    try:
        data = request.json
        job_id = data.get('job_id')
        captions = data.get('captions', [])
        
        if not job_id:
            return jsonify({'error': 'Job ID required'}), 400
        
        # Verify access
        job = get_job_from_db(job_id, user)
        if not job or not can_access_job(job, user, session):
            return jsonify({'error': 'Access denied'}), 403
        
        # Start caption update task
        regen_job_id = f"regen_{secrets.token_urlsafe(8)}"
        
        socketio.start_background_task(
            update_captions_task,
            job_id, captions, regen_job_id,
            user.id if user else None,
            session.get('session_id')
        )
        
        return jsonify({
            'message': 'Caption update started',
            'regeneration_job_id': regen_job_id
        })
        
    except Exception as e:
        logger.error(f"Update captions error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload_to_youtube', methods=['POST'])
@auth_required
def upload_to_youtube(user):
    """Upload clip to YouTube"""
    try:
        data = request.json
        job_id = data.get('job_id')
        title = data.get('title')
        description = data.get('description', '')
        privacy_status = data.get('privacy_status', 'private')
        
        if not all([job_id, title]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Get clip data
        clip_data = get_clip_data(job_id, user)
        if not clip_data:
            return jsonify({'error': 'Clip not found'}), 404
        
        # TODO: Implement YouTube upload
        # For now, return mock response
        return jsonify({
            'message': 'Upload successful',
            'url': 'https://youtube.com/watch?v=mock_video_id'
        })
        
    except Exception as e:
        logger.error(f"YouTube upload error: {e}")
        return jsonify({'error': str(e)}), 500

# --- Static File Routes ---

@app.route('/clips/<path:filename>')
@auth_optional
def serve_clip(filename, user):
    """Serve clip files with access control"""
    # Extract job_id from filename
    job_id = filename.split('_')[3] if 'clip_' in filename else None
    
    if job_id:
        # Verify access
        job = get_job_from_db(job_id, user)
        if job and can_access_job(job, user, session):
            return send_from_directory('clips', filename)
    
    return jsonify({'error': 'Access denied'}), 403

# ==================== SOCKET.IO EVENTS ====================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    # Get job_id from query params if available
    job_id = request.args.get('job_id')
    if job_id:
        join_room(job_id)
        emit('connected', {'room': job_id, 'type': 'job'})
    else:
        # Join user or session room
        user = User.get_from_session(session)
        if user:
            room = f"user_{user.id}"
        else:
            room = f"session_{session.get('session_id', 'anonymous')}"
        join_room(room)
        emit('connected', {'room': room, 'type': 'user'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info("Client disconnected")

# ==================== BACKGROUND TASKS ====================

def process_video_task(job_id, url, duration, start_time, end_time, user_id, session_id):
    """Background task to process video"""
    try:
        # Update job status
        active_jobs[job_id]['status'] = 'processing'
        
        # Define progress callback
        def progress_callback(progress, message):
            active_jobs[job_id]['progress'] = progress
            active_jobs[job_id]['message'] = message
            
            socketio.emit('progress_update', {
                'job_id': job_id,
                'progress': progress,
                'message': message,
                'status': 'processing'
            }, room=job_id)
        
        # Process video
        result = process_youtube_video(
            url=url,
            target_duration=duration,
            start_time=start_time,
            end_time=end_time,
            progress_callback=progress_callback
        )
        
        if result['success']:
            # Update job with results
            active_jobs[job_id].update({
                'status': 'completed',
                'progress': 100,
                'clip_data': result['clip_data'],
                'message': 'Clip generated successfully!'
            })
            
            # Save to database
            save_clip_to_db(job_id, result['clip_data'], user_id, session_id)
            
            # Emit completion
            socketio.emit('clip_completed', {
                'job_id': job_id,
                'clip_data': result['clip_data'],
                'captions': result['clip_data'].get('captions', [])
            }, room=job_id)
            
        else:
            raise Exception(result.get('error', 'Unknown error'))
            
    except Exception as e:
        logger.error(f"Video processing error: {e}")
        active_jobs[job_id].update({
            'status': 'error',
            'error': str(e),
            'message': f'Error: {str(e)}'
        })
        
        socketio.emit('progress_update', {
            'job_id': job_id,
            'status': 'error',
            'message': str(e)
        }, room=job_id)

def update_captions_task(job_id, captions, regen_job_id, user_id, session_id):
    """Background task to update captions"""
    try:
        # Define progress callback
        def progress_callback(progress, message):
            socketio.emit('regeneration_update', {
                'job_id': job_id,
                'regeneration_job_id': regen_job_id,
                'progress': progress,
                'message': message
            }, room=job_id)
        
        # Update captions
        result = update_captions_for_job(job_id, captions, progress_callback)
        
        if result['success']:
            # Update clip data in database
            update_clip_captions_db(job_id, result['updated_captions'])
            
            socketio.emit('regeneration_complete', {
                'job_id': job_id,
                'regeneration_job_id': regen_job_id,
                'message': 'Captions updated successfully!'
            }, room=job_id)
        else:
            raise Exception(result.get('error', 'Caption update failed'))
            
    except Exception as e:
        logger.error(f"Caption update error: {e}")
        socketio.emit('regeneration_error', {
            'job_id': job_id,
            'regeneration_job_id': regen_job_id,
            'error': str(e)
        }, room=job_id)

# ==================== DATABASE HELPERS ====================

def get_job_from_db(job_id, user):
    """Get job data from database"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM clips 
            WHERE job_id = ?
        """, (job_id,))
        
        row = cursor.fetchone()
        if row:
            # Convert row to dict
            columns = [desc[0] for desc in cursor.description]
            job_data = dict(zip(columns, row))
            
            # Parse JSON fields
            if job_data.get('clip_data'):
                job_data['clip_data'] = json.loads(job_data['clip_data'])
            
            return job_data
        return None
    finally:
        conn.close()

def save_clip_to_db(job_id, clip_data, user_id, session_id):
    """Save clip data to database"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO clips (
                job_id, user_id, session_id, video_url, 
                clip_path, clip_data, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            job_id,
            user_id,
            session_id,
            clip_data.get('original_url'),
            clip_data.get('path'),
            json.dumps(clip_data),
            datetime.now()
        ))
        conn.commit()
    finally:
        conn.close()

def get_clip_data(job_id, user):
    """Get clip data with proper access control"""
    job = active_jobs.get(job_id)
    if not job:
        job = get_job_from_db(job_id, user)
    
    if job and can_access_job(job, user, session):
        return job.get('clip_data')
    return None

def can_access_job(job, user, session):
    """Check if user can access job"""
    if not job:
        return False
    
    # User owns it
    if user and job.get('user_id') == user.id:
        return True
    
    # Session owns it (anonymous)
    if job.get('session_id') == session.get('session_id'):
        return True
    
    return False

def get_anonymous_clips_count(session):
    """Get count of anonymous clips for session"""
    session_id = session.get('session_id')
    if not session_id:
        return 0
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM clips 
            WHERE session_id = ? AND user_id IS NULL
        """, (session_id,))
        return cursor.fetchone()[0]
    finally:
        conn.close()

def convert_anonymous_clips(session, user_id):
    """Convert anonymous clips to user clips"""
    session_id = session.get('session_id')
    if not session_id:
        return
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE clips 
            SET user_id = ?, session_id = NULL 
            WHERE session_id = ? AND user_id IS NULL
        """, (user_id, session_id))
        conn.commit()
        
        logger.info(f"Converted {cursor.rowcount} anonymous clips to user {user_id}")
    finally:
        conn.close()

def get_user_clips(user_id, limit=10):
    """Get user's recent clips"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT job_id, video_url, clip_data, created_at 
            FROM clips 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (user_id, limit))
        
        clips = []
        for row in cursor.fetchall():
            clip_data = json.loads(row[2]) if row[2] else {}
            clips.append({
                'job_id': row[0],
                'original_title': clip_data.get('original_title', 'Untitled'),
                'duration': clip_data.get('duration', 30),
                'created_at': row[3]
            })
        
        return clips
    finally:
        conn.close()

def update_clip_captions_db(job_id, captions):
    """Update clip captions in database"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Get existing clip data
        cursor.execute("SELECT clip_data FROM clips WHERE job_id = ?", (job_id,))
        row = cursor.fetchone()
        if row:
            clip_data = json.loads(row[0])
            clip_data['captions'] = captions
            
            # Update
            cursor.execute("""
                UPDATE clips 
                SET clip_data = ?, updated_at = ? 
                WHERE job_id = ?
            """, (json.dumps(clip_data), datetime.now(), job_id))
            conn.commit()
    finally:
        conn.close()

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {e}")
    return render_template('500.html'), 500

# ==================== MAIN ====================

if __name__ == '__main__':
    # Run storage cleanup on startup
    storage_optimizer.cleanup()
    
    # Start scheduler for periodic cleanup
    socketio.start_background_task(
        target=lambda: storage_optimizer.run_periodic_cleanup(
            callback=lambda msg: logger.info(f"Storage cleanup: {msg}")
        )
    )
    
    # Run the app
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
