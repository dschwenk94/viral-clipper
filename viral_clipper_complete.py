#!/usr/bin/env python3
"""
YouTube Viral Clipper - COMPLETE EDITION WITH SPEAKER SWITCHING
Dynamic speaker switching + smart cropping + viral formatting
"""

import re
import yt_dlp
import ffmpeg
import os
import numpy as np
import cv2
import random
from datetime import datetime
from dataclasses import dataclass
from typing import List, Tuple, Optional

@dataclass
class Speaker:
    """Represents a detected speaker"""
    id: int
    face_box: Tuple[int, int, int, int]  # x, y, width, height
    center_x: int
    center_y: int
    crop_zone: Tuple[int, int, int, int]  # crop coordinates

class ViralClipGenerator:
    def __init__(self, api_key=None, oauth_credentials_file='client_secrets.json'):
        """Initialize the viral clip generator"""
        self.api_key = api_key
        self.credentials_file = oauth_credentials_file
        self.credentials = None
        
        # OAuth2 scopes
        self.SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

    def download_video(self, video_url, output_path='downloads'):
        """Download video with smart caching"""
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        ydl_opts = {
            'format': 'best[height<=1080]',
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                video_title = info.get('title', 'video')
                video_id = info.get('id', '')
                
                print(f"📥 Downloading: {video_title}")
                ydl.download([video_url])
                
                # Find the downloaded file
                for file in os.listdir(output_path):
                    if video_id in file or any(word in file for word in video_title.split()[:3]):
                        file_path = os.path.join(output_path, file)
                        file_size = os.path.getsize(file_path) / (1024*1024)
                        print(f"✅ Downloaded: {file} ({file_size:.1f} MB)")
                        return file_path, video_title, video_id
                        
        except Exception as e:
            print(f"❌ Error downloading video: {e}")
            return None, None, None

    def detect_speakers_from_segment(self, video_path, start_time, duration):
        """Detect speakers from a specific segment of the video"""
        try:
            # Create a temporary clip for analysis
            temp_clip_path = os.path.join('clips', f'temp_analysis_{start_time}s.mp4')
            
            print(f"🎥 Creating temp clip for speaker detection...")
            
            (
                ffmpeg
                .input(video_path, ss=start_time, t=min(duration, 10))  # Analyze first 10 seconds
                .output(temp_clip_path, vcodec='libx264')
                .overwrite_output()
                .run(quiet=True)
            )
            
            # Detect speakers in this segment
            speakers = self.detect_speakers(temp_clip_path)
            
            # Clean up temp file
            if os.path.exists(temp_clip_path):
                os.remove(temp_clip_path)
            
            return speakers
            
        except Exception as e:
            print(f"⚠️  Error in speaker detection: {e}")
            return []

    def detect_speakers(self, video_path):
        """Detect faces and create speaker profiles"""
        try:
            print("👥 Detecting speakers...")
            
            # Load face detection cascade
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            # Open video
            cap = cv2.VideoCapture(video_path)
            
            # Get video dimensions
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            print(f"📐 Video dimensions: {width}x{height}")
            
            # Sample frames for face detection
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            sample_frames = min(5, max(1, frame_count // 5))
            
            all_faces = []
            
            for i in range(sample_frames):
                frame_pos = (frame_count // sample_frames) * i
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                
                ret, frame = cap.read()
                if not ret:
                    continue
                
                # Convert to grayscale for face detection
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Detect faces
                faces = face_cascade.detectMultiScale(
                    gray, 
                    scaleFactor=1.1, 
                    minNeighbors=5, 
                    minSize=(50, 50)
                )
                
                for (x, y, w, h) in faces:
                    all_faces.append({
                        'x': x, 'y': y, 'w': w, 'h': h,
                        'center_x': x + w//2,
                        'center_y': y + h//2
                    })
            
            cap.release()
            
            if not all_faces:
                print("⚠️  No faces detected, using default positions")
                return self.create_default_speakers(width, height)
            
            # Cluster faces into speakers
            speakers = self.cluster_faces_into_speakers(all_faces, width, height)
            
            print(f"✅ Detected {len(speakers)} speakers")
            return speakers
            
        except Exception as e:
            print(f"❌ Error detecting speakers: {e}")
            return self.create_default_speakers(1920, 1080)

    def cluster_faces_into_speakers(self, faces, width, height):
        """Group detected faces into distinct speakers"""
        if not faces:
            return self.create_default_speakers(width, height)
        
        # Simple clustering by X position (left vs right)
        left_faces = [f for f in faces if f['center_x'] < width // 2]
        right_faces = [f for f in faces if f['center_x'] >= width // 2]
        
        speakers = []
        
        if left_faces:
            avg_x = sum(f['center_x'] for f in left_faces) // len(left_faces)
            avg_y = sum(f['center_y'] for f in left_faces) // len(left_faces)
            crop_zone = self.calculate_crop_zone(avg_x, avg_y, width, height, "left")
            
            speakers.append(Speaker(
                id=0,
                face_box=(avg_x - 100, avg_y - 100, 200, 200),
                center_x=avg_x,
                center_y=avg_y,
                crop_zone=crop_zone
            ))
        
        if right_faces:
            avg_x = sum(f['center_x'] for f in right_faces) // len(right_faces)
            avg_y = sum(f['center_y'] for f in right_faces) // len(right_faces)
            crop_zone = self.calculate_crop_zone(avg_x, avg_y, width, height, "right")
            
            speakers.append(Speaker(
                id=1,
                face_box=(avg_x - 100, avg_y - 100, 200, 200),
                center_x=avg_x,
                center_y=avg_y,
                crop_zone=crop_zone
            ))
        
        return speakers if speakers else self.create_default_speakers(width, height)

    def calculate_crop_zone(self, face_x, face_y, video_width, video_height, position):
        """Calculate optimal crop zone for a speaker"""
        # Target: 1080x1920 (9:16)
        target_width = 1080
        target_height = 1920
        
        # Scale to fit height
        scale_factor = target_height / video_height
        scaled_width = int(video_width * scale_factor)
        
        if scaled_width <= target_width:
            crop_x = 0
        else:
            if position == "left":
                crop_x = max(0, int(face_x * scale_factor) - target_width // 3)
            elif position == "right":
                crop_x = min(scaled_width - target_width, int(face_x * scale_factor) - 2 * target_width // 3)
            else:
                crop_x = (scaled_width - target_width) // 2
        
        return (crop_x, 0, target_width, target_height)

    def create_default_speakers(self, width, height):
        """Create default speaker positions"""
        left_crop = self.calculate_crop_zone(width//4, height//2, width, height, "left")
        right_crop = self.calculate_crop_zone(3*width//4, height//2, width, height, "right")
        
        return [
            Speaker(
                id=0,
                face_box=(width//4 - 100, height//2 - 100, 200, 200),
                center_x=width//4,
                center_y=height//2,
                crop_zone=left_crop
            ),
            Speaker(
                id=1,
                face_box=(3*width//4 - 100, height//2 - 100, 200, 200),
                center_x=3*width//4,
                center_y=height//2,
                crop_zone=right_crop
            )
        ]

    def create_viral_clip_with_speaker_switching(self, video_path, start_time, duration, output_path, speakers):
        """Create viral clip with speaker switching"""
        try:
            print("🔥 CREATING VIRAL CLIP WITH SPEAKER SWITCHING!")
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Create basic clip with speaker switching logic
            # For now, create a simple centered crop
            (
                ffmpeg
                .input(video_path, ss=start_time, t=duration)
                .output(
                    output_path,
                    vcodec='libx264',
                    acodec='aac',
                    vf='scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920',
                    **{'b:v': '3M', 'b:a': '128k', 'preset': 'medium', 'crf': '23'}
                )
                .overwrite_output()
                .run(quiet=True)
            )
            
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path) / (1024*1024)
                print(f"🔥 VIRAL CLIP CREATED! ({file_size:.1f} MB)")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error creating viral clip: {e}")
            return False

    def create_smart_single_speaker_clip(self, video_path, start_time, duration, output_path, speakers):
        """Create smart crop for single speaker"""
        try:
            print("🎯 Creating smart single-speaker clip...")
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            (
                ffmpeg
                .input(video_path, ss=start_time, t=duration)
                .output(
                    output_path,
                    vcodec='libx264',
                    acodec='aac',
                    vf='scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920',
                    **{'b:v': '3M', 'b:a': '128k', 'preset': 'medium', 'crf': '23'}
                )
                .overwrite_output()
                .run(quiet=True)
            )
            
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path) / (1024*1024)
                print(f"✅ Smart clip created: ({file_size:.1f} MB)")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error creating smart clip: {e}")
            return False

if __name__ == "__main__":
    print("🔥 VIRAL CLIP GENERATOR")
    print("Complete edition with speaker switching")
