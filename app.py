#!/usr/bin/env python3
"""
🎯 VIRAL CLIPPER WEB APP 🎯 - FIXED VERSION WITH OAUTH
Flask web application for the viral clip generator with:
1. Refresh button maintaining state
2. Pop-out effect color consistency
3. Full YouTube OAuth integration and upload
"""

from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect, url_for
from flask_socketio import SocketIO, emit
import os
import json
import uuid
import threading
import time
import pickle
from datetime import datetime
from auto_peak_viral_clipper import AutoPeakViralClipper
from caption_fragment_fix import merge_fragmented_captions
from ass_caption_update_system_v2 import ASSCaptionUpdateSystemV2

# OAuth imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

app = Flask(__name__)
app.config['SECRET_KEY'] = 'viral_clipper_secret_key_2025'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize the clipper with ASS captions
clipper = AutoPeakViralClipper()

# Store active jobs
active_jobs = {}

# OAuth configuration
OAUTH_SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
CREDENTIALS_FILE = 'client_secrets.json'
TOKEN_FILE = 'token.pickle'

# Global OAuth service
youtube_upload_service = None
oauth_credentials = None

# OAuth Helper Functions
def check_oauth_status():
    """Check if OAuth credentials are valid"""
    global oauth_credentials, youtube_upload_service
    
    try:
        creds = None
        
        # Load existing credentials
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)
        
        # Check if credentials are valid
        if creds and creds.valid:
            oauth_credentials = creds
            youtube_upload_service = build('youtube', 'v3', credentials=creds)
            return {
                'authenticated': True,
                'status': 'valid',
                'message': 'OAuth credentials are valid'
            }
        elif creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                oauth_credentials = creds
                youtube_upload_service = build('youtube', 'v3', credentials=creds)
                
                # Save refreshed credentials
                with open(TOKEN_FILE, 'wb') as token:
                    pickle.dump(creds, token)
                
                return {
                    'authenticated': True,
                    'status': 'refreshed',
                    'message': 'OAuth credentials refreshed successfully'
                }
            except Exception as e:
                return {
                    'authenticated': False,
                    'status': 'expired',
                    'message': f'Failed to refresh credentials: {str(e)}'
                }
        else:
            return {
                'authenticated': False,
                'status': 'missing',
                'message': 'No valid OAuth credentials found'
            }
            
    except Exception as e:
        return {
            'authenticated': False,
            'status': 'error',
            'message': f'OAuth check failed: {str(e)}'
        }

def initiate_oauth_flow():
    """Start OAuth authentication flow"""
    try:
        if not os.path.exists(CREDENTIALS_FILE):
            return {
                'success': False,
                'error': 'OAuth credentials file not found. Please ensure client_secrets.json exists.'
            }
        
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, OAUTH_SCOPES)
        
        # Run local server for OAuth callback
        creds = flow.run_local_server(
            port=0,
            prompt='consent',
            open_browser=True
        )
        
        if creds:
            # Save credentials
            with open(TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)
            
            # Update global variables
            global oauth_credentials, youtube_upload_service
            oauth_credentials = creds
            youtube_upload_service = build('youtube', 'v3', credentials=creds)
            
            return {
                'success': True,
                'message': 'OAuth authentication successful!'
            }
        else:
            return {
                'success': False,
                'error': 'OAuth authentication failed'
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f'OAuth flow error: {str(e)}'
        }

def upload_video_to_youtube(video_path, title, description, privacy_status='private'):
    """Upload video to YouTube using OAuth credentials"""
    global youtube_upload_service
    
    if not youtube_upload_service:
        return {
            'success': False,
            'error': 'YouTube service not authenticated. Please authenticate first.'
        }
    
    try:
        # Prepare video metadata
        tags = ['Shorts', 'Viral', 'Clips', 'AI', 'AutoGenerated']
        
        body = {
            'snippet': {
                'title': title[:100],  # YouTube title limit
                'description': f"{description}\n\n#Shorts"[:5000],  # Description limit
                'tags': tags,
                'categoryId': '22',  # People & Blogs
                'defaultLanguage': 'en',
                'defaultAudioLanguage': 'en'
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': False,
                'madeForKids': False
            }
        }
        
        # Create upload media
        media = MediaFileUpload(
            video_path,
            chunksize=-1,
            resumable=True,
            mimetype='video/*'
        )
        
        # Execute upload
        insert_request = youtube_upload_service.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )
        
        response = resumable_upload_with_progress(insert_request)
        
        if response and 'id' in response:
            video_id = response['id']
            return {
                'success': True,
                'video_id': video_id,
                'url': f'https://www.youtube.com/watch?v={video_id}',
                'message': f'Successfully uploaded: {title}'
            }
        else:
            return {
                'success': False,
                'error': 'Upload completed but no video ID returned'
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f'Upload failed: {str(e)}'
        }

def resumable_upload_with_progress(insert_request):
    """Handle resumable upload with progress tracking"""
    response = None
    error = None
    retry = 0
    
    while response is None:
        try:
            status, response = insert_request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                print(f"Upload progress: {progress}%")
                # Could emit socket event here for real-time progress
                
        except Exception as e:
            error = e
            if retry < 3:
                retry += 1
                print(f"Upload error, retrying ({retry}/3): {error}")
                time.sleep(2 ** retry)
            else:
                print(f"Upload failed after 3 retries: {error}")
                break
    
    return response

class ClipJob:
    """Represents a clip generation job"""
    def __init__(self, job_id, url, duration, start_time=None, end_time=None):
        self.job_id = job_id
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
        # 🆕 Hybrid approach fields
        self.regeneration_status = None  # 'processing', 'completed', 'failed'
        self.regeneration_progress = 0
        self.regeneration_job_id = None

def update_job_progress(job_id, status, progress, message):
    """Update job progress and emit to frontend"""
    if job_id in active_jobs:
        job = active_jobs[job_id]
        job.status = status
        job.progress = progress
        job.message = message
        
        socketio.emit('progress_update', {
            'job_id': job_id,
            'status': status,
            'progress': progress,
            'message': message
        })

def process_clip_generation(job_id):
    """Background thread for clip generation"""
    try:
        job = active_jobs[job_id]
        
        update_job_progress(job_id, "processing", 5, "Starting clip generation...")
        
        # Calculate actual start time for processing
        if job.start_time is not None and job.end_time is not None:
            # Manual time selection
            actual_start_time = job.start_time
            actual_duration = job.end_time - job.start_time
            update_job_progress(job_id, "processing", 10, "Using manual time selection...")
        else:
            # Auto-detection
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
            })
        else:
            job.error = "Clip generation failed"
            update_job_progress(job_id, "error", 0, "Clip generation failed")
            
    except Exception as e:
        job.error = str(e)
        update_job_progress(job_id, "error", 0, f"Error: {str(e)}")

def extract_caption_data(clip_data):
    """🔧 FIXED: Extract caption data from both SRT and ASS files"""
    print("🔧 CAPTION EXTRACTION: Starting caption extraction...")
    
    subtitle_file = clip_data.get('subtitle_file')
    if not subtitle_file:
        print("❌ No subtitle_file in clip_data")
        print(f"📊 Available clip_data keys: {list(clip_data.keys())}")
        return []
    
    print(f"📁 Subtitle file path: {subtitle_file}")
    
    if not os.path.exists(subtitle_file):
        print(f"❌ Subtitle file does not exist: {subtitle_file}")
        
        # Try to find subtitle files in the clips directory
        video_path = clip_data.get('path', '')
        if video_path:
            base_name = os.path.splitext(video_path)[0]
            
            # Try different subtitle file extensions
            for ext in ['.srt', '.ass']:
                potential_subtitle = base_name + '_captions' + ext
                print(f"🔍 Checking for: {potential_subtitle}")
                if os.path.exists(potential_subtitle):
                    print(f"✅ Found subtitle file: {potential_subtitle}")
                    subtitle_file = potential_subtitle
                    break
            else:
                print("❌ No subtitle files found")
                return []
        else:
            print("❌ No video path in clip_data")
            return []
    
    print(f"📝 Processing subtitle file: {os.path.basename(subtitle_file)}")
    
    # Determine file type and extract accordingly
    if subtitle_file.endswith('.srt'):
        print("🎯 Extracting from SRT file...")
        captions = extract_captions_from_srt_fixed(subtitle_file)
    elif subtitle_file.endswith('.ass'):
        print("🎯 Extracting from ASS file...")
        captions = extract_captions_from_ass_fixed(subtitle_file)
    else:
        print(f"❌ Unknown subtitle format: {subtitle_file}")
        return []
    
    if not captions:
        print("❌ No captions extracted")
        return []
    
    # Convert to web app format
    web_captions = []
    for i, caption in enumerate(captions):
        web_caption = {
            'index': i,
            'text': caption.get('text', '').strip(),
            'speaker': caption.get('speaker', 'Speaker 1'),
            'start_time': caption.get('start_time', '0:00:00.00'),
            'end_time': caption.get('end_time', '0:00:00.00')
        }
        web_captions.append(web_caption)
        print(f"   {i+1}. {web_caption['speaker']}: '{web_caption['text'][:40]}{'...' if len(web_caption['text']) > 40 else ''}'")
    
    print(f"✅ Successfully extracted {len(web_captions)} captions for web app")
    return web_captions

def extract_captions_from_srt_fixed(srt_file_path: str):
    """🔧 FIXED: Extract captions from SRT file"""
    captions = []
    
    try:
        print(f"   📖 Reading SRT file: {os.path.basename(srt_file_path)}")
        
        with open(srt_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"   📄 File size: {len(content)} characters")
        
        # Parse SRT format - handle both \\n\\n and real newlines
        content = content.replace('\\n', '\n')  # Fix escaped newlines
        subtitle_blocks = content.strip().split('\n\n')
        
        print(f"   🔢 Found {len(subtitle_blocks)} subtitle blocks")
        
        for i, block in enumerate(subtitle_blocks):
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                try:
                    index = int(lines[0])
                    timing = lines[1]
                    text = '\n'.join(lines[2:])
                    
                    # Parse timing (HH:MM:SS,mmm --> HH:MM:SS,mmm)
                    if ' --> ' in timing:
                        start_time_str, end_time_str = timing.split(' --> ')
                        
                        # Extract speaker if present
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
                        
                except Exception as e:
                    print(f"   ⚠️ Skipping malformed block {i}: {e}")
                    continue
        
        print(f"   ✅ Extracted {len(captions)} captions from SRT")
        return captions
        
    except Exception as e:
        print(f"   ❌ Error reading SRT file: {e}")
        import traceback
        traceback.print_exc()
        return []

def extract_captions_from_ass_fixed(ass_file_path: str):
    """🔧 FIXED: Extract captions from ASS file"""
    captions = []
    
    try:
        print(f"   📖 Reading ASS file: {os.path.basename(ass_file_path)}")
        
        with open(ass_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"   📄 File has {len(lines)} lines")
        
        # Find dialogue lines
        dialogue_count = 0
        for line in lines:
            line = line.strip()
            if line.startswith('Dialogue:'):
                dialogue_count += 1
                try:
                    # Parse ASS dialogue format:
                    # Dialogue: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
                    parts = line.split(',', 9)
                    if len(parts) >= 10:
                        start_time = parts[1]
                        end_time = parts[2]
                        speaker = parts[3] if parts[3] else 'Speaker 1'
                        text = parts[9]
                        
                        # Clean up text (remove ASS formatting codes)
                        import re
                        text = re.sub(r'{[^}]*}', '', text)  # Remove {formatting}
                        text = text.strip()
                        
                        if text:  # Only add non-empty captions
                            captions.append({
                                'text': text,
                                'speaker': speaker,
                                'start_time': start_time,
                                'end_time': end_time,
                                'index': len(captions)
                            })
                            
                except Exception as e:
                    print(f"   ⚠️ Error parsing dialogue line: {e}")
                    continue
        
        print(f"   📊 Found {dialogue_count} dialogue lines, extracted {len(captions)} valid captions")
        return captions
        
    except Exception as e:
        print(f"   ❌ Error reading ASS file: {e}")
        import traceback
        traceback.print_exc()
        return []

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/generate_clip', methods=['POST'])
def generate_clip():
    """Start clip generation process"""
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
    job = ClipJob(job_id, url, duration, start_time, end_time)
    active_jobs[job_id] = job
    
    # Start background processing
    thread = threading.Thread(target=process_clip_generation, args=(job_id,))
    thread.daemon = True
    thread.start()
    
    return jsonify({'job_id': job_id, 'status': 'started'})

@app.route('/api/job_status/<job_id>')
def job_status(job_id):
    """Get job status"""
    if job_id not in active_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = active_jobs[job_id]
    return jsonify({
        'job_id': job_id,
        'status': job.status,
        'progress': job.progress,
        'message': job.message,
        'clip_data': job.clip_data,
        'error': job.error
    })

@app.route('/api/regeneration_status/<job_id>')
def regeneration_status(job_id):
    """Get regeneration status for a job"""
    if job_id not in active_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = active_jobs[job_id]
    return jsonify({
        'job_id': job_id,
        'regeneration_status': job.regeneration_status,
        'regeneration_progress': job.regeneration_progress,
        'video_path': job.clip_data['path'] if job.clip_data else None
    })

@app.route('/api/back_to_input', methods=['POST'])
def back_to_input():
    """Go back to input screen and clear current job"""
    data = request.json
    job_id = data.get('job_id')
    
    if job_id in active_jobs:
        # Clean up the job
        del active_jobs[job_id]
    
    return jsonify({'status': 'success', 'message': 'Returned to input screen'})

# 🆕 NEW: Clear all jobs endpoint
@app.route('/api/clear_all_jobs', methods=['POST'])
def clear_all_jobs():
    """Clear all active jobs and reset application state"""
    global active_jobs
    
    try:
        # Clear all active jobs
        job_count = len(active_jobs)
        active_jobs.clear()
        
        print(f"🧺 Cleared {job_count} active jobs")
        
        return jsonify({
            'status': 'success', 
            'message': f'Cleared {job_count} active jobs',
            'jobs_cleared': job_count
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to clear jobs: {str(e)}'}), 500

# 🆕 NEW: Get application state endpoint
@app.route('/api/app_state')
def get_app_state():
    """Get current application state for debugging"""
    try:
        state = {
            'active_jobs_count': len(active_jobs),
            'active_job_ids': list(active_jobs.keys()),
            'active_job_urls': {job_id: job.url for job_id, job in active_jobs.items()}
        }
        
        return jsonify(state)
        
    except Exception as e:
        return jsonify({'error': f'Failed to get app state: {str(e)}'}), 500

# 🔧 FIX #1: New endpoint for refreshing video while staying on caption screen
@app.route('/api/refresh_video/<job_id>')
def refresh_video(job_id):
    """Refresh video data without changing screens"""
    if job_id not in active_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = active_jobs[job_id]
    if not job.clip_data:
        return jsonify({'error': 'No clip data available'}), 400
    
    # Re-extract caption data to get latest updates
    caption_data = extract_caption_data(job.clip_data)
    job.clip_data['captions'] = caption_data
    
    # Add cache-busting timestamp to video URL
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

# OAuth API Endpoints
@app.route('/api/oauth/status')
def oauth_status():
    """Check OAuth authentication status"""
    status = check_oauth_status()
    return jsonify(status)

@app.route('/api/oauth/authenticate', methods=['POST'])
def oauth_authenticate():
    """Start OAuth authentication flow"""
    try:
        result = initiate_oauth_flow()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Authentication failed: {str(e)}'
        }), 500

@app.route('/api/oauth/revoke', methods=['POST'])
def oauth_revoke():
    """Revoke OAuth credentials"""
    try:
        global oauth_credentials, youtube_upload_service
        
        # Remove token file
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)
        
        # Clear global variables
        oauth_credentials = None
        youtube_upload_service = None
        
        return jsonify({
            'success': True,
            'message': 'OAuth credentials revoked successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to revoke credentials: {str(e)}'
        }), 500

@app.route('/api/upload_to_youtube', methods=['POST'])
def upload_to_youtube():
    """Upload clip to YouTube using OAuth"""
    data = request.json
    job_id = data.get('job_id')
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    privacy_status = data.get('privacy_status', 'private')  # private, unlisted, public
    
    if job_id not in active_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = active_jobs[job_id]
    if not job.clip_data:
        return jsonify({'error': 'No clip available for upload'}), 400
    
    if not title:
        return jsonify({'error': 'Title is required'}), 400
    
    # Check OAuth status first
    oauth_status = check_oauth_status()
    if not oauth_status['authenticated']:
        return jsonify({
            'error': 'YouTube authentication required',
            'oauth_status': oauth_status
        }), 401
    
    try:
        video_path = job.clip_data['path']
        
        if not os.path.exists(video_path):
            return jsonify({'error': 'Video file not found'}), 404
        
        # Upload to YouTube
        upload_result = upload_video_to_youtube(
            video_path=video_path,
            title=title,
            description=description,
            privacy_status=privacy_status
        )
        
        if upload_result['success']:
            # Update job data with upload info
            job.clip_data['youtube_upload'] = {
                'video_id': upload_result['video_id'],
                'url': upload_result['url'],
                'uploaded_at': datetime.now().isoformat(),
                'title': title,
                'privacy_status': privacy_status
            }
            
            return jsonify({
                'status': 'success',
                'message': upload_result['message'],
                'video_id': upload_result['video_id'],
                'url': upload_result['url'],
                'privacy_status': privacy_status
            })
        else:
            return jsonify({
                'error': upload_result['error']
            }), 500
        
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/clips/<filename>')
def serve_clip(filename):
    """Serve video clips"""
    return send_from_directory('clips', filename)

@app.route('/api/test_upload', methods=['POST'])
def test_upload():
    """Test YouTube upload credentials without actually uploading"""
    try:
        oauth_status = check_oauth_status()
        
        if not oauth_status['authenticated']:
            return jsonify({
                'success': False,
                'error': 'Not authenticated',
                'oauth_status': oauth_status
            })
        
        # Test API access by getting channel info
        if youtube_upload_service:
            try:
                channels_response = youtube_upload_service.channels().list(
                    part='snippet',
                    mine=True
                ).execute()
                
                if channels_response.get('items'):
                    channel = channels_response['items'][0]['snippet']
                    return jsonify({
                        'success': True,
                        'message': 'YouTube API access confirmed',
                        'channel_title': channel.get('title', 'Unknown'),
                        'oauth_status': oauth_status
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'No channel found for authenticated user'
                    })
                    
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'API test failed: {str(e)}'
                })
        else:
            return jsonify({
                'success': False,
                'error': 'YouTube service not initialized'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Test failed: {str(e)}'
        }), 500

def format_seconds_to_mmss(seconds):
    """Convert seconds to MM:SS format"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}:{secs:02d}"

def parse_time_to_seconds(time_str):
    """Convert MM:SS or seconds to seconds"""
    if not time_str:
        return None
    
    time_str = str(time_str).strip()
    
    if ':' in time_str:
        # MM:SS format
        parts = time_str.split(':')
        if len(parts) == 2:
            try:
                minutes = int(parts[0])
                seconds = int(parts[1])
                return minutes * 60 + seconds
            except ValueError:
                return None
    else:
        # Just seconds
        try:
            return float(time_str)
        except ValueError:
            return None
    
    return None

def regenerate_video_background_ass(job_id, updated_captions):
    """🆕 ASS: Background thread for video regeneration using ASS caption system"""
    try:
        job = active_jobs[job_id]
        original_clip_data = job.clip_data
        
        # Update regeneration status
        job.regeneration_status = 'processing'
        job.regeneration_progress = 10
        
        # Emit progress update
        socketio.emit('regeneration_update', {
            'job_id': job_id,
            'status': 'processing',
            'progress': 10,
            'message': '🎯 ASS: Creating captions using ASS system...'
        })
        
        # Step 1: Get paths
        subtitle_file = original_clip_data.get('subtitle_file')
        original_video_path = original_clip_data['path']
        
        if not subtitle_file:
            raise Exception('Caption file not found')
        
        job.regeneration_progress = 30
        socketio.emit('regeneration_update', {
            'job_id': job_id,
            'status': 'processing',
            'progress': 30,
            'message': '📝 Using ASS caption system...'
        })
        
        # Step 2: Use ASS caption system to update captions
        success = clipper.update_captions_ass(subtitle_file, updated_captions)
        
        if not success:
            raise Exception('Failed to update captions using ASS system')
        
        job.regeneration_progress = 50
        socketio.emit('regeneration_update', {
            'job_id': job_id,
            'status': 'processing',
            'progress': 50,
            'message': '🎬 Creating video with updated captions...'
        })
        
        # Step 3: Create video with updated ASS captions
        temp_ass_path = original_video_path.replace('.mp4', '_ASS_temp.mp4')
        
        # CRITICAL: We need the video WITHOUT captions
        # Look for the original switching video (before captions were added)
        base_video_path = original_video_path.replace('.mp4', '_temp_switching.mp4')
        
        # If the temp switching video doesn't exist, try other options
        if not os.path.exists(base_video_path):
            # Try looking for a backup without captions
            no_caption_path = original_video_path.replace('.mp4', '_no_captions.mp4')
            if os.path.exists(no_caption_path):
                base_video_path = no_caption_path
            else:
                # As a last resort, we'd need to recreate the video without captions
                # For now, log a warning
                print("⚠️ WARNING: Cannot find video without captions!")
                print("⚠️ This will result in overlapping captions.")
                base_video_path = original_video_path
        
        job.regeneration_progress = 70
        socketio.emit('regeneration_update', {
            'job_id': job_id,
            'status': 'processing',
            'progress': 70,
            'message': '🔥 Burning ASS captions into video...'
        })
        
        # Step 4: Burn updated ASS captions
        success = clipper.burn_captions_into_video_debug(
            base_video_path,  # Use the video WITHOUT captions
            subtitle_file,    # Updated subtitle file
            temp_ass_path     # New output
        )
        
        if not success:
            raise Exception('Failed to burn ASS captions into video')
        
        job.regeneration_progress = 90
        socketio.emit('regeneration_update', {
            'job_id': job_id,
            'status': 'processing',
            'progress': 90,
            'message': '✅ Finalizing ASS caption video...'
        })
        
        # Step 5: Replace original with updated version
        if os.path.exists(original_video_path):
            os.remove(original_video_path)
            print(f"🗑️ Removed old video: {os.path.basename(original_video_path)}")
        
        os.rename(temp_ass_path, original_video_path)
        print(f"✅ Replaced with ASS caption video: {os.path.basename(original_video_path)}")
        
        # Step 6: Update job data
        job.clip_data['updated_at'] = datetime.now().isoformat()
        job.clip_data['caption_updates'] = len(updated_captions)
        job.clip_data['ass_captions_applied'] = True
        
        # Complete regeneration
        job.regeneration_status = 'completed'
        job.regeneration_progress = 100
        
        socketio.emit('regeneration_complete', {
            'job_id': job_id,
            'status': 'completed',
            'progress': 100,
            'message': '🎉 ASS: Video updated with captions!',
            'updated_path': original_video_path
        })
        
        print(f"🎉 ASS: Video regeneration completed for job {job_id} using ASS system!")
        
    except Exception as e:
        print(f"❌ ASS video regeneration failed for job {job_id}: {e}")
        
        if job_id in active_jobs:
            job = active_jobs[job_id]
            job.regeneration_status = 'failed'
            job.regeneration_progress = 0
            
            socketio.emit('regeneration_error', {
                'job_id': job_id,
                'status': 'failed',
                'error': f'ASS regeneration failed: {str(e)}'
            })

# 🔧 FIX #2: Fixed ASS file creation with proper pop-out effect colors
def create_updated_ass_file_fixed(original_subtitle_path, updated_captions):
    """🔧 FIXED: Create updated ASS file without caption overlaps"""
    try:
        print(f"🔧 FIXING OVERLAPS: Creating clean ASS file from {os.path.basename(original_subtitle_path)}")
        
        # Read original ASS file
        with open(original_subtitle_path, 'r', encoding='utf-8') as f:
            ass_lines = f.readlines()
        
        # Parse the ASS file structure to preserve header and styles
        header_lines = []
        styles_section = []
        events_start_idx = -1
        format_line_idx = -1
        
        for i, line in enumerate(ass_lines):
            line_stripped = line.strip()
            
            if line_stripped == '[Events]':
                events_start_idx = i
                header_lines.append(line)
                continue
            elif line_stripped.startswith('Format:') and events_start_idx != -1:
                format_line_idx = i
                header_lines.append(line)
                break  # Stop after format line
            elif line_stripped.startswith('Style:'):
                styles_section.append(line_stripped)
                header_lines.append(line)
            elif events_start_idx == -1:  # Before [Events] section
                header_lines.append(line)
        
        if events_start_idx == -1 or format_line_idx == -1:
            raise Exception('Could not find [Events] section or Format line in ASS file')
        
        # Extract speaker colors from styles
        speaker_colors = parse_speaker_colors_from_styles(styles_section)
        print(f"🎨 Extracted speaker colors: {speaker_colors}")
        
        # Sort updated captions by index to maintain order
        sorted_captions = sorted(updated_captions, key=lambda x: x.get('index', 0))
        print(f"📝 Processing {len(sorted_captions)} updated captions in order")
        
        # Create NEW dialogue lines with NON-OVERLAPPING timing
        new_dialogue_lines = []
        
        # Calculate timing parameters
        caption_duration = 1.8    # Each caption shows for 1.8 seconds
        gap_duration = 0.2        # 0.2 second gap between captions
        
        for i, caption in enumerate(sorted_captions):
            speaker_name = caption.get('speaker', 'Speaker 1')
            text = caption.get('text', '').strip()
            
            if not text:  # Skip empty captions
                continue
            
            # Calculate NON-OVERLAPPING timing - this is the key fix!
            start_time = i * (caption_duration + gap_duration)
            end_time = start_time + caption_duration
            
            # Format timing for ASS (H:MM:SS.CC format)
            start_ass = seconds_to_ass_time_fixed(start_time)
            end_ass = seconds_to_ass_time_fixed(end_time)
            
            # Get speaker color
            speaker_color = speaker_colors.get(speaker_name, "&H000045FF")
            
            # Create CLEAN pop-out effect without escaping issues
            pop_effect = r"{\fad(150,100)\t(0,300,\fscx110\fscy110)\t(300,400,\fscx100\fscy100)\c" + speaker_color + r"}"
            
            # Format viral words cleanly
            formatted_text = format_viral_words_clean_fixed(text, speaker_color)
            
            # Create dialogue line with proper formatting
            dialogue_line = f"Dialogue: 0,{start_ass},{end_ass},{speaker_name},,0,0,0,,{pop_effect}{formatted_text}\n"
            new_dialogue_lines.append(dialogue_line)
            
            print(f"✏️  Caption {i+1}: {speaker_name} ({start_ass}-{end_ass}) -> '{text[:30]}{'...' if len(text) > 30 else ''}'")
        
        # Build complete new ASS file
        new_ass_content = "".join(header_lines)
        new_ass_content += "".join(new_dialogue_lines)
        
        # Write updated ASS file with clear naming
        updated_subtitle_path = original_subtitle_path.replace('.ass', '_CLEAN_FIXED.ass')
        
        with open(updated_subtitle_path, 'w', encoding='utf-8') as f:
            f.write(new_ass_content)
        
        print(f"✅ FIXED: Created clean ASS file without overlaps: {os.path.basename(updated_subtitle_path)}")
        print(f"📊 Generated {len(new_dialogue_lines)} dialogue lines with non-overlapping timing")
        
        # Verify the file was created correctly
        if os.path.exists(updated_subtitle_path):
            file_size = os.path.getsize(updated_subtitle_path)
            print(f"📁 File size: {file_size} bytes")
            return updated_subtitle_path
        else:
            print("❌ File was not created successfully")
            return None
        
    except Exception as e:
        print(f"❌ Error creating clean ASS file: {e}")
        import traceback
        traceback.print_exc()
        return None

def parse_speaker_colors_from_styles(styles_section):
    """Parse speaker colors from ASS style definitions"""
    speaker_colors = {}
    
    for style_line in styles_section:
        if style_line.startswith('Style:'):
            # Parse: Style: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour...
            parts = style_line.split(',')
            if len(parts) >= 4:
                speaker_name = parts[0].replace('Style: ', '').strip()
                primary_color = parts[3].strip()  # This is the ASS color format
                speaker_colors[speaker_name] = primary_color
                print(f"🎨 Parsed {speaker_name}: {primary_color}")
    
    return speaker_colors

def create_fixed_pop_effect(speaker_name, speaker_colors):
    """Create pop-out effect that uses the speaker's actual color"""
    # Get speaker's color, fallback to default
    speaker_color = speaker_colors.get(speaker_name, "&H00FF4500")  # Default orange
    
    # Create pop-out effect with fade-in and scaling, using speaker's color
    pop_effect = f"{{\\fad(100,50)\\t(0,200,\\fscx120\\fscy120)\\t(200,300,\\fscx100\\fscy100)\\c{speaker_color}}}"
    
    return pop_effect

def format_viral_words_with_speaker_color(text, speaker_name, speaker_colors):
    """Format viral words using speaker's actual color instead of hardcoded color"""
    viral_keywords = [
        'fucking', 'shit', 'damn', 'crazy', 'insane', 'ridiculous',
        'amazing', 'incredible', 'awesome', 'epic', 'legendary'
    ]
    
    # Get speaker's color for viral word formatting
    speaker_color = speaker_colors.get(speaker_name, "&H00FF4500")  # Default orange
    
    formatted_text = text
    for word in viral_keywords:
        if word.lower() in text.lower():
            # 🔧 FIXED: Use speaker's color instead of hardcoded color, and proper reset
            viral_format = f"{{\\\\c{speaker_color}\\\\fs26}}{word.upper()}{{\\\\r\\\\c{speaker_color}}}"
            
            import re
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            formatted_text = pattern.sub(viral_format, formatted_text)
    
    return formatted_text

def seconds_to_ass_time_fixed(seconds):
    """Convert seconds to ASS time format (H:MM:SS.CC)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centiseconds = int((seconds % 1) * 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{centiseconds:02d}"

def format_viral_words_clean_fixed(text, speaker_color):
    """Format viral words with CLEAN formatting (no double escaping)"""
    viral_keywords = [
        'fucking', 'shit', 'damn', 'crazy', 'insane', 'ridiculous',
        'amazing', 'incredible', 'awesome', 'epic', 'legendary'
    ]
    
    formatted_text = text
    for word in viral_keywords:
        if word.lower() in text.lower():
            # FIXED: Raw string to avoid escape issues
            viral_format = r"{\c" + speaker_color + r"\fs24\b1}" + word.upper() + r"{\r\c" + speaker_color + r"}"
            
            import re
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            # Use raw string replacement to avoid escape issues
            formatted_text = pattern.sub(lambda m: viral_format, formatted_text)
    
    return formatted_text

def get_original_video_path(clip_data):
    """Get the path to the original video without captions (for regeneration)"""
    # For now, we'll use the current path and assume it's the source
    # In a more sophisticated system, we might keep the pre-caption video
    return clip_data['path']

@app.route('/api/update_captions', methods=['POST'])
def update_captions():
    """🆕 HYBRID APPROACH: Update captions with live preview + background regeneration"""
    data = request.json
    job_id = data.get('job_id')
    captions = data.get('captions', [])
    
    if job_id not in active_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = active_jobs[job_id]
    if not job.clip_data:
        return jsonify({'error': 'No clip data available'}), 400
    
    try:
        # Preprocess captions to fix fragmentation
        print(f"🔍 Checking {len(captions)} captions for fragmentation...")
        avg_text_length = sum(len(c.get('text', '')) for c in captions) / len(captions) if captions else 0
        
        if avg_text_length < 5:  # Only merge if VERY fragmented (was 20)
            print("⚠️ Detected fragmented captions from frontend, merging...")
            captions = merge_fragmented_captions(captions)
            print(f"✅ Merged to {len(captions)} proper captions")
            
            # Log the merged captions for debugging
            for i, cap in enumerate(captions[:5]):  # Show first 5
                print(f"  {i+1}. {cap.get('speaker', 'Unknown')}: {cap.get('text', '')[:50]}...")
        
        # Start background regeneration with ASS system
        regeneration_thread = threading.Thread(
            target=regenerate_video_background_ass, 
            args=(job_id, captions)
        )
        regeneration_thread.daemon = True
        regeneration_thread.start()
        
        # Return immediately with success (hybrid approach)
        return jsonify({
            'status': 'success', 
            'message': 'Caption update started. Video is being regenerated in background.',
            'regeneration_started': True
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to start caption update: {str(e)}'}), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

if __name__ == '__main__':
    # Ensure clips directory exists
    os.makedirs('clips', exist_ok=True)
    
    # Initialize OAuth on startup
    print("🔐 Checking OAuth status...")
    oauth_status = check_oauth_status()
    if oauth_status['authenticated']:
        print(f"✅ OAuth: {oauth_status['message']}")
    else:
        print(f"⚠️  OAuth: {oauth_status['message']}")
        print("   📝 You'll need to authenticate via the web interface to upload videos")
    
    # Run the app
    print("🎯 Starting Viral Clipper Web App with OAuth...")
    print("🌐 Access at: http://localhost:5000")
    print("📤 YouTube upload: " + ("Ready" if oauth_status['authenticated'] else "Requires authentication"))
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
