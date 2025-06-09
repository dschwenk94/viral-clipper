"""
TikTok API Client for Clippy
Handles TikTok Content Posting API operations
"""

import os
import json
import logging
import time
from typing import Optional, Dict, List, Tuple
from pathlib import Path

import requests

logger = logging.getLogger(__name__)


class TikTokAPIClient:
    """Client for TikTok Content Posting API"""
    
    # TikTok API endpoints
    BASE_URL = 'https://open.tiktokapis.com/v2'
    UPLOAD_BASE_URL = 'https://open-upload.tiktokapis.com'
    
    # Endpoints
    CREATOR_INFO_URL = f'{BASE_URL}/post/publish/creator_info/query/'
    VIDEO_INIT_URL = f'{BASE_URL}/post/publish/video/init/'
    DIRECT_POST_INIT_URL = f'{BASE_URL}/post/publish/inbox/video/init/'
    PUBLISH_STATUS_URL = f'{BASE_URL}/post/publish/status/fetch/'
    CANCEL_PUBLISH_URL = f'{BASE_URL}/post/publish/cancel/'
    
    # Video constraints
    MAX_VIDEO_SIZE = 4 * 1024 * 1024 * 1024  # 4GB
    MIN_VIDEO_SIZE = 1024  # 1KB
    MAX_DURATION = 10 * 60  # 10 minutes
    MIN_DURATION = 3  # 3 seconds
    
    # Chunk upload constraints
    MIN_CHUNK_SIZE = 5 * 1024 * 1024  # 5MB
    MAX_CHUNK_SIZE = 64 * 1024 * 1024  # 64MB
    MAX_FINAL_CHUNK_SIZE = 128 * 1024 * 1024  # 128MB
    
    def __init__(self, access_token: str):
        """
        Initialize TikTok API client
        
        Args:
            access_token: Valid TikTok access token
        """
        self.access_token = access_token
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    
    def get_creator_info(self) -> Optional[Dict]:
        """
        Get creator information and posting capabilities
        
        Returns:
            Creator info dict or None if failed
        """
        try:
            response = requests.post(
                self.CREATOR_INFO_URL,
                headers=self.headers,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('error', {}).get('code') == 'ok':
                creator_info = data.get('data', {})
                logger.info(f"Retrieved creator info for: {creator_info.get('creator_username')}")
                return creator_info
            else:
                logger.error(f"Failed to get creator info: {data}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting creator info: {e}")
            return None
    
    def init_video_upload(
        self,
        video_path: str,
        title: str,
        description: str = "",
        privacy_level: str = "SELF_ONLY",
        allow_comments: bool = True,
        allow_duet: bool = True,
        allow_stitch: bool = True,
        direct_post: bool = False
    ) -> Optional[Dict]:
        """
        Initialize video upload to TikTok
        
        Args:
            video_path: Path to video file
            title: Video title (max 150 chars)
            description: Video description
            privacy_level: One of PUBLIC_TO_EVERYONE, MUTUAL_FOLLOW_FRIENDS, SELF_ONLY
            allow_comments: Whether to allow comments
            allow_duet: Whether to allow duets
            allow_stitch: Whether to allow stitches
            direct_post: If True, post directly; if False, save as draft
            
        Returns:
            Upload initialization response or None if failed
        """
        # Validate video file
        if not os.path.exists(video_path):
            logger.error(f"Video file not found: {video_path}")
            return None
        
        video_size = os.path.getsize(video_path)
        if video_size < self.MIN_VIDEO_SIZE or video_size > self.MAX_VIDEO_SIZE:
            logger.error(f"Video size {video_size} bytes is out of allowed range")
            return None
        
        # Calculate chunks
        chunk_size = min(self.MAX_CHUNK_SIZE, max(self.MIN_CHUNK_SIZE, video_size // 10))
        total_chunks = (video_size + chunk_size - 1) // chunk_size
        
        # Prepare request data
        post_data = {
            "post_info": {
                "title": title[:150],  # TikTok limit
                "privacy_level": privacy_level,
                "disable_comment": not allow_comments,
                "disable_duet": not allow_duet,
                "disable_stitch": not allow_stitch
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": video_size,
                "chunk_size": chunk_size,
                "total_chunk_count": total_chunks
            }
        }
        
        # Add description if provided
        if description:
            post_data["post_info"]["description"] = description
        
        # Choose endpoint based on posting mode
        url = self.VIDEO_INIT_URL if direct_post else self.DIRECT_POST_INIT_URL
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=post_data,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('error', {}).get('code') == 'ok':
                upload_info = data.get('data', {})
                upload_info['video_path'] = video_path
                upload_info['chunk_size'] = chunk_size
                upload_info['total_chunks'] = total_chunks
                upload_info['video_size'] = video_size
                
                logger.info(f"Initialized TikTok upload: {upload_info.get('publish_id')}")
                return upload_info
            else:
                logger.error(f"Failed to initialize upload: {data}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error initializing upload: {e}")
            return None
    
    def upload_video_chunks(
        self,
        upload_info: Dict,
        progress_callback: Optional[callable] = None
    ) -> bool:
        """
        Upload video file in chunks
        
        Args:
            upload_info: Upload info from init_video_upload
            progress_callback: Optional callback for progress updates
            
        Returns:
            True if successful, False otherwise
        """
        video_path = upload_info['video_path']
        upload_url = upload_info['upload_url']
        chunk_size = upload_info['chunk_size']
        total_chunks = upload_info['total_chunks']
        video_size = upload_info['video_size']
        
        try:
            with open(video_path, 'rb') as video_file:
                for chunk_num in range(total_chunks):
                    # Calculate chunk boundaries
                    start_byte = chunk_num * chunk_size
                    
                    # Last chunk can be larger (up to 128MB)
                    if chunk_num == total_chunks - 1:
                        end_byte = video_size - 1
                        current_chunk_size = video_size - start_byte
                    else:
                        end_byte = start_byte + chunk_size - 1
                        current_chunk_size = chunk_size
                    
                    # Read chunk data
                    video_file.seek(start_byte)
                    chunk_data = video_file.read(current_chunk_size)
                    
                    # Upload chunk
                    headers = {
                        'Content-Range': f'bytes {start_byte}-{end_byte}/{video_size}',
                        'Content-Type': 'video/mp4',
                        'Content-Length': str(len(chunk_data))
                    }
                    
                    response = requests.put(
                        upload_url,
                        headers=headers,
                        data=chunk_data,
                        timeout=300  # 5 minutes for large chunks
                    )
                    
                    response.raise_for_status()
                    
                    # Update progress
                    if progress_callback:
                        progress = ((chunk_num + 1) / total_chunks) * 100
                        progress_callback(progress, f"Uploaded chunk {chunk_num + 1}/{total_chunks}")
                    
                    logger.info(f"Uploaded chunk {chunk_num + 1}/{total_chunks}")
            
            logger.info("Successfully uploaded all video chunks")
            return True
            
        except Exception as e:
            logger.error(f"Error uploading video chunks: {e}")
            return False
    
    def get_publish_status(self, publish_id: str) -> Optional[Dict]:
        """
        Check the status of a video upload/publish
        
        Args:
            publish_id: Publish ID from init_video_upload
            
        Returns:
            Status dict or None if failed
        """
        try:
            response = requests.post(
                self.PUBLISH_STATUS_URL,
                headers=self.headers,
                json={"publish_id": publish_id},
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('error', {}).get('code') == 'ok':
                return data.get('data', {})
            else:
                logger.error(f"Failed to get publish status: {data}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting publish status: {e}")
            return None
    
    def wait_for_publish(
        self,
        publish_id: str,
        timeout: int = 300,
        progress_callback: Optional[callable] = None
    ) -> Optional[Dict]:
        """
        Wait for video to finish processing
        
        Args:
            publish_id: Publish ID to check
            timeout: Maximum seconds to wait
            progress_callback: Optional callback for status updates
            
        Returns:
            Final status dict or None if failed/timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.get_publish_status(publish_id)
            
            if not status:
                return None
            
            publish_status = status.get('publish_status', {})
            status_code = publish_status.get('publish_status_code')
            
            if progress_callback:
                progress_callback(
                    status_code,
                    f"Status: {status_code}"
                )
            
            # Check for completion
            if status_code == 'PUBLISH_COMPLETE':
                logger.info(f"Video published successfully: {status.get('share_url')}")
                return status
            elif status_code in ['FAILED', 'CANCEL']:
                logger.error(f"Video publish failed: {publish_status.get('fail_reason')}")
                return None
            
            # Still processing
            time.sleep(5)
        
        logger.error(f"Timeout waiting for video publish after {timeout} seconds")
        return None
    
    def cancel_publish(self, publish_id: str) -> bool:
        """
        Cancel a video upload/publish
        
        Args:
            publish_id: Publish ID to cancel
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.post(
                self.CANCEL_PUBLISH_URL,
                headers=self.headers,
                json={"publish_id": publish_id},
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('error', {}).get('code') == 'ok':
                logger.info(f"Successfully cancelled publish: {publish_id}")
                return True
            else:
                logger.error(f"Failed to cancel publish: {data}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error cancelling publish: {e}")
            return False
    
    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str = "",
        privacy_level: str = "SELF_ONLY",
        allow_comments: bool = True,
        allow_duet: bool = True,
        allow_stitch: bool = True,
        direct_post: bool = False,
        progress_callback: Optional[callable] = None
    ) -> Optional[Dict]:
        """
        Complete video upload workflow
        
        Args:
            video_path: Path to video file
            title: Video title
            description: Video description
            privacy_level: Privacy setting
            allow_comments: Whether to allow comments
            allow_duet: Whether to allow duets
            allow_stitch: Whether to allow stitches
            direct_post: If True, post directly; if False, save as draft
            progress_callback: Optional callback for progress updates
            
        Returns:
            Final publish status or None if failed
        """
        # Initialize upload
        if progress_callback:
            progress_callback(0, "Initializing upload...")
        
        upload_info = self.init_video_upload(
            video_path=video_path,
            title=title,
            description=description,
            privacy_level=privacy_level,
            allow_comments=allow_comments,
            allow_duet=allow_duet,
            allow_stitch=allow_stitch,
            direct_post=direct_post
        )
        
        if not upload_info:
            return None
        
        publish_id = upload_info.get('publish_id')
        
        # Upload video chunks
        if progress_callback:
            progress_callback(10, "Uploading video...")
        
        if not self.upload_video_chunks(upload_info, progress_callback):
            self.cancel_publish(publish_id)
            return None
        
        # Wait for processing
        if progress_callback:
            progress_callback(90, "Processing video...")
        
        return self.wait_for_publish(publish_id, progress_callback=progress_callback)
