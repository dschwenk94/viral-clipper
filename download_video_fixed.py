def download_video(self, video_url, output_path='downloads'):
    """Download video with smart caching and improved YouTube compatibility"""
    # Import storage optimizer
    from storage_optimizer import StorageOptimizer
    
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    # Initialize storage optimizer
    optimizer = StorageOptimizer(downloads_dir=output_path)
    
    # Check if video already exists
    existing_path, existing_title, video_id = optimizer.check_existing_download(video_url)
    if existing_path:
        return existing_path, existing_title, video_id
    
    # If not found, download it with improved options
    ydl_opts = {
        'format': 'best[height<=1080]/best',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        # Additional options to bypass restrictions
        'cookiesfrombrowser': 'chrome',  # Use browser cookies
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'referer': 'https://www.youtube.com/',
        # Retry options
        'retries': 10,
        'fragment_retries': 10,
        'skip_download': False,
        # Use alternative extractors if needed
        'extractor_args': {'youtube': {'player_skip': ['configs', 'webpage']}},
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # First try to extract info
            info = ydl.extract_info(video_url, download=False)
            video_title = info.get('title', 'video')
            video_id = info.get('id', '')
            
            print(f"📥 Downloading: {video_title}")
            
            # Try to download
            try:
                ydl.download([video_url])
            except Exception as e:
                print(f"⚠️  First attempt failed: {e}")
                print("🔄 Trying alternative method...")
                
                # Try with simpler format selection
                ydl_opts['format'] = 'best'
                with yt_dlp.YoutubeDL(ydl_opts) as ydl2:
                    ydl2.download([video_url])
            
            # Find the downloaded file
            for file in os.listdir(output_path):
                if video_id in file or any(word in file for word in video_title.split()[:3]):
                    file_path = os.path.join(output_path, file)
                    file_size = os.path.getsize(file_path) / (1024*1024)
                    print(f"✅ Downloaded: {file} ({file_size:.1f} MB)")
                    
                    # Add to cache
                    optimizer.add_to_cache(video_url, file_path, video_title)
                    
                    return file_path, video_title, video_id
                    
    except Exception as e:
        print(f"❌ Error downloading video: {e}")
        
        # Final fallback: try youtube-dl command line
        print("🔄 Attempting fallback download method...")
        try:
            import subprocess
            output_template = os.path.join(output_path, '%(title)s.%(ext)s')
            cmd = [
                'yt-dlp',
                '--no-check-certificate',
                '-f', 'best',
                '-o', output_template,
                video_url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                # Try to find the downloaded file again
                for file in os.listdir(output_path):
                    if os.path.isfile(os.path.join(output_path, file)) and file.endswith(('.mp4', '.webm', '.mkv')):
                        file_path = os.path.join(output_path, file)
                        print(f"✅ Downloaded via fallback: {file}")
                        return file_path, file, video_id or 'unknown'
            else:
                print(f"❌ Fallback failed: {result.stderr}")
                
        except Exception as fallback_error:
            print(f"❌ Fallback error: {fallback_error}")
    
    return None, None, None
