#!/usr/bin/env python3
"""
🎯 AUTO-PEAK VIRAL CLIPPER - SRT INTEGRATION 🎯
Updated to use SRT subtitles instead of problematic ASS format
"""

import os
import json
import ffmpeg
import random
import cv2
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

# Import our systems
from viral_clipper_complete import ViralClipGenerator as BaseClipGenerator, Speaker
from enhanced_heuristic_peak_detector import EnhancedHeuristicPeakDetector, ViralMoment
from srt_viral_caption_system import SRTViralCaptionSystem

@dataclass
class PhraseSegment:
    """Phrase with timing and speaker info"""
    phrase: str
    start_time: float
    end_time: float
    speaker_id: int
    speaker_name: str
    speaker_color: str
    is_viral: bool

@dataclass
class SpeakerProfile:
    """Speaker profile with visual and caption info"""
    id: int
    name: str
    color: str
    word_count: int
    speaking_time: float
    crop_zone: Optional[Tuple[int, int, int, int]] = None

class AutoPeakViralClipperSRT(BaseClipGenerator):
    """🎯 AUTO-PEAK: With SRT subtitles for reliable caption display"""
    
    def __init__(self, api_key=None, oauth_credentials_file='client_secrets.json'):
        """Initialize the auto-peak viral clipper with SRT captions"""
        super().__init__(api_key, oauth_credentials_file)
        
        # Initialize peak detector
        self.peak_detector = EnhancedHeuristicPeakDetector()
        
        # 🆕 Initialize SRT caption system
        self.caption_system = SRTViralCaptionSystem()
        
        # Enhanced color palette
        self.speaker_colors = [
            "#FF4500",   # Speaker 1 - Fire Red/Orange
            "#00BFFF",   # Speaker 2 - Electric Blue  
            "#00FF88"    # Speaker 3 - Neon Green (if needed)
        ]
        self.speaker_names = ["Speaker 1", "Speaker 2", "Speaker 3"]
        
        # Create configs directory
        self.config_dir = "configs"
        os.makedirs(self.config_dir, exist_ok=True)
        
        print("🎯 AUTO-PEAK VIRAL CLIPPER INITIALIZED")
        print("✅ Automatic peak detection: ENABLED")
        print("✅ Enhanced heuristics: ENABLED")
        print("✅ Speaker switching + SRT captions: ENABLED")
    
    def generate_auto_peak_viral_clip(self, video_url: str, duration: int = 30, manual_start_time: Optional[float] = None):
        """
        🎯 MAIN FUNCTION: Auto-detect optimal moment and create viral clip with SRT captions
        """
        print("🎯 GENERATING AUTO-PEAK VIRAL CLIP WITH SRT CAPTIONS!")
        print("🚀 Finding optimal moment + Creating viral clip!")
        print("=" * 80)
        
        # Step 1: Download video
        print("📥 Step 1: Downloading video...")
        video_path, video_title, video_id = self.download_video(video_url)
        if not video_path:
            print("❌ Video download failed")
            return None
        print(f"✅ Video downloaded: {os.path.basename(video_path)}")
        
        # Step 2: Find optimal moment (or use manual override)
        if manual_start_time is not None:
            print(f"\\n🎯 Step 2: Using manual start time: {manual_start_time}s")
            optimal_moment = None
            start_time = manual_start_time
            confidence = 0.5  # Default confidence for manual selection
            
        else:
            print("\\n🎯 Step 2: Auto-detecting optimal viral moment...")
            optimal_moment = self.peak_detector.find_optimal_viral_moment(video_path, duration)
            
            if not optimal_moment:
                print("⚠️  Auto-detection failed, using fallback heuristics...")
                start_time = self.get_fallback_start_time(video_path)
                confidence = 0.3
            else:
                start_time = optimal_moment.timestamp
                confidence = optimal_moment.confidence
                
                print("\\n🎉 OPTIMAL MOMENT DETECTED!")
                print(f"   ⏰ Best timestamp: {start_time:.1f}s ({start_time/60:.1f} min)")
                print(f"   🎯 Confidence: {confidence:.2f}")
                print(f"   💡 Reason: {optimal_moment.reason}")
        
        # Step 3: Detect speakers for video cropping
        print("\\n👥 Step 3: Detecting speakers for video cropping...")
        video_speakers = self.detect_speakers_from_segment(video_path, start_time, duration)
        print(f"✅ Video speakers detected: {len(video_speakers)}")
        
        # Step 4: Get simplified captions (no complex phrase tracking)
        print("\\n🎤 Step 4: Getting simplified transcription for SRT captions...")
        simple_captions = self.get_simple_transcription(video_path, start_time, duration)
        
        if not simple_captions:
            print("❌ No captions generated")
            return None
        
        print(f"✅ Simple captions created: {len(simple_captions)}")
        
        # Step 5: Create speaker switching video
        print("\\n🎬 Step 5: Creating speaker switching video...")
        clip_filename = f"auto_peak_clip_{video_id}_{int(start_time)}s.mp4"
        clip_path = os.path.join('clips', clip_filename)
        temp_video_path = clip_path.replace('.mp4', '_temp_switching.mp4')
        
        if len(video_speakers) >= 2:
            print("🎯 Multiple speakers detected - creating dynamic switching video!")
            video_success = self.create_viral_clip_with_speaker_switching(
                video_path, start_time, duration, temp_video_path, video_speakers
            )
        else:
            print("⚠️  Single/no speakers - using smart crop")
            video_success = self.create_smart_single_speaker_clip(
                video_path, start_time, duration, temp_video_path, video_speakers
            )
        
        if not video_success:
            print("❌ Video creation failed")
            return None
        print(f"✅ Base video created: {os.path.basename(temp_video_path)}")
        
        # Step 6: Generate SRT captions
        print("\\n📝 Step 6: Generating SRT captions...")
        subtitle_path = clip_path.replace('.mp4', '_captions.srt')  # Use .srt extension
        
        # 🆕 USE SRT CAPTION SYSTEM
        subtitle_success = self.caption_system.generate_srt_file(
            simple_captions, subtitle_path, duration
        )
        
        if not subtitle_success:
            print("❌ SRT subtitle generation failed - using video without captions")
            if os.path.exists(temp_video_path):
                os.rename(temp_video_path, clip_path)
            captions_added = False
        else:
            print(f"✅ SRT subtitle file created: {os.path.basename(subtitle_path)}")
            
            # Step 7: Burn in SRT captions
            print("\\n🔥 Step 7: Burning in SRT captions...")
            caption_success = self.burn_srt_captions_into_video(temp_video_path, subtitle_path, clip_path)
            
            if not caption_success:
                print("❌ SRT caption burning failed - using video without captions")
                if os.path.exists(temp_video_path):
                    os.rename(temp_video_path, clip_path)
                captions_added = False
            else:
                print("✅ SRT captions burned into video successfully!")
                # Clean up temp video
                if os.path.exists(temp_video_path):
                    os.remove(temp_video_path)
                captions_added = True
        
        # Step 8: Report results
        if os.path.exists(clip_path):
            file_size = os.path.getsize(clip_path) / (1024*1024)
            
            print("\\n🎉 AUTO-PEAK VIRAL CLIP WITH SRT CAPTIONS CREATED!")
            print(f"✅ Output: {clip_path} ({file_size:.1f} MB)")
            print(f"📊 AUTO-PEAK STATS:")
            print(f"   ⏰ Optimal timestamp: {start_time:.1f}s ({start_time/60:.1f} min)")
            print(f"   🎯 Detection confidence: {confidence:.2f}")
            print(f"   ⏱️  Duration: {duration}s")
            print(f"   👥 Video speakers: {len(video_speakers)} (for cropping)")
            print(f"   📝 SRT captions: {len(simple_captions)}")
            print(f"   🔄 Speaker switching: {len(video_speakers) >= 2}")
            print(f"   🎨 Captions added: {captions_added}")
            
            if optimal_moment:
                print(f"   🔥 Detection signals: {', '.join(optimal_moment.signals[:3])}")
                print(f"   💡 Peak reason: {optimal_moment.reason[:60]}...")
            
            return {
                'path': clip_path,
                'video_id': video_id,
                'original_title': video_title,
                'optimal_timestamp': start_time,
                'detection_confidence': confidence,
                'duration': duration,
                'video_speakers': len(video_speakers),
                'caption_speakers': len(set(cap['speaker'] for cap in simple_captions)),
                'speaker_switching': len(video_speakers) >= 2,
                'phrase_segments': len(simple_captions),
                'captions_added': captions_added,
                'subtitle_file': subtitle_path if captions_added else None,
                'file_size_mb': file_size,
                'created_at': datetime.now().isoformat(),
                'auto_detected': manual_start_time is None,
                'peak_signals': optimal_moment.signals if optimal_moment else [],
                'peak_reason': optimal_moment.reason if optimal_moment else "Manual selection",
                'caption_format': 'srt'  # Indicate we're using SRT
            }
        else:
            print("❌ Output file not created")
            return None
    
    def get_simple_transcription(self, video_path: str, start_time: float, duration: float) -> List[Dict]:
        """Get simplified transcription that works with the SRT system"""
        try:
            import whisper
            
            print("   🎤 Extracting audio for transcription...")
            # Extract audio
            audio_filename = f"srt_transcription_{int(start_time)}s_{duration}s.wav"
            audio_path = os.path.join('clips', audio_filename)
            
            (
                ffmpeg
                .input(video_path, ss=start_time, t=duration)
                .output(
                    audio_path,
                    acodec='pcm_s16le',
                    ac=1,
                    ar='16000'
                )
                .overwrite_output()
                .run(quiet=True)
            )
            
            if not os.path.exists(audio_path):
                print("   ❌ Audio extraction failed")
                return []
            
            print("   🧠 Running Whisper transcription...")
            # Transcribe with segments (not word-level for simplicity)
            model = whisper.load_model("base")
            result = model.transcribe(audio_path, language='en')
            
            # Convert to simple caption format
            simple_captions = []
            
            for i, segment in enumerate(result["segments"]):
                text = segment["text"].strip()
                if not text:
                    continue
                
                # Intelligent speaker assignment (simplified)
                speaker = self.assign_speaker_simple(text, i, len(result["segments"]))
                
                simple_captions.append({
                    'text': text,
                    'speaker': speaker,
                    'index': i,
                    'original_start': segment["start"],
                    'original_end': segment["end"]
                })
            
            # Clean up
            if os.path.exists(audio_path):
                os.remove(audio_path)
            
            print(f"   ✅ Generated {len(simple_captions)} simple captions for SRT")
            return simple_captions
            
        except Exception as e:
            print(f"   ❌ Simple transcription failed: {e}")
            return []
    
    def assign_speaker_simple(self, text: str, segment_index: int, total_segments: int) -> str:
        """Simple speaker assignment based on content and position"""
        text_lower = text.lower()
        
        # Assign based on content patterns
        aggressive_words = ["fucking", "shit", "damn", "crazy", "insane", "ridiculous", "what the hell"]
        if any(word in text_lower for word in aggressive_words):
            return "Speaker 1"  # Assign aggressive content to Speaker 1
        
        # Questions often go to Speaker 1
        if "?" in text or any(text_lower.startswith(start) for start in ["what", "why", "how", "is", "was", "did"]):
            return "Speaker 1"
        
        # Longer responses to Speaker 2
        if len(text.split()) > 8:
            return "Speaker 2"
        
        # Alternate based on position (simple back-and-forth)
        if segment_index % 2 == 0:
            return "Speaker 1"
        else:
            return "Speaker 2"
    
    def get_fallback_start_time(self, video_path: str) -> float:
        """Get fallback start time if auto-detection fails"""
        try:
            # Get video duration
            probe = ffmpeg.probe(video_path)
            duration = float(probe['format']['duration'])
            
            # Use simple heuristics
            if duration > 1800:  # 30+ minutes (podcast)
                return 300  # 5 minutes in
            elif duration > 600:  # 10+ minutes
                return 180  # 3 minutes in
            else:  # Short content
                return duration * 0.3  # 30% through
                
        except:
            return 300  # Default fallback
    
    def burn_srt_captions_into_video(self, video_path: str, subtitle_path: str, output_path: str) -> bool:
        """Burn SRT captions into video with proper formatting"""
        try:
            if not os.path.exists(video_path):
                print(f"   ❌ Video file not found: {video_path}")
                return False
                
            if not os.path.exists(subtitle_path):
                print(f"   ❌ SRT file not found: {subtitle_path}")
                return False
            
            print(f"   🔥 Burning SRT captions: {os.path.basename(subtitle_path)} -> {os.path.basename(output_path)}")
            
            abs_video_path = os.path.abspath(video_path)
            abs_subtitle_path = os.path.abspath(subtitle_path)
            abs_output_path = os.path.abspath(output_path)
            
            # Use subtitles filter for SRT (different from ASS)
            (
                ffmpeg
                .input(abs_video_path)
                .output(
                    abs_output_path,
                    vcodec='libx264',
                    acodec='aac',
                    vf=f"subtitles={abs_subtitle_path}:force_style='FontName=Arial Black,FontSize=24,PrimaryColour=&Hffffff,OutlineColour=&H000000,Outline=2,Shadow=1,Alignment=2,MarginV=50'",
                    **{'b:v': '3M', 'b:a': '128k', 'preset': 'medium', 'crf': '23'}
                )
                .overwrite_output()
                .run(quiet=True)
            )
            
            success = os.path.exists(output_path)
            if success:
                print(f"   ✅ SRT caption burning successful!")
            else:
                print(f"   ❌ SRT caption burning failed - output file not created")
            
            return success
            
        except Exception as e:
            print(f"   ❌ Error burning SRT captions: {e}")
            return False
    
    # 🆕 NEW METHOD: Update captions using SRT system (for web app)
    def update_captions_srt(self, subtitle_path: str, updated_captions: List[Dict], duration: float = 30.0) -> bool:
        """Update captions using the SRT caption system"""
        try:
            print("🔄 Updating captions using SRT system...")
            return self.caption_system.update_captions_from_web_input_srt(
                subtitle_path, updated_captions, duration
            )
        except Exception as e:
            print(f"❌ Error updating SRT captions: {e}")
            return False


def test_srt_integration():
    """Test the SRT caption integration"""
    print("🎯 TESTING SRT CAPTION INTEGRATION")
    print("=" * 60)
    
    # Use existing downloaded video if available
    downloads_dir = "downloads"
    test_video = None
    
    if os.path.exists(downloads_dir):
        for file in os.listdir(downloads_dir):
            if file.endswith('.mp4'):
                test_video = os.path.join(downloads_dir, file)
                break
    
    if not test_video:
        print("❌ No test video found in downloads directory")
        print("💡 Please download a video first or provide a YouTube URL")
        return
    
    print(f"🎬 Testing with: {os.path.basename(test_video)}")
    
    # Initialize clipper with SRT captions
    clipper = AutoPeakViralClipperSRT()
    
    # Test simple transcription
    print("\\n🎤 Testing simple transcription for SRT...")
    simple_captions = clipper.get_simple_transcription(test_video, 300, 20)  # 20-second test
    
    if simple_captions:
        print(f"✅ Simple transcription successful: {len(simple_captions)} captions")
        for i, cap in enumerate(simple_captions[:3]):  # Show first 3
            print(f"   {i+1}. {cap['speaker']}: '{cap['text'][:50]}{'...' if len(cap['text']) > 50 else ''}'")
        
        # Test SRT generation
        print("\\n📝 Testing SRT generation...")
        test_srt_path = "clips/test_srt_integration.srt"
        
        success = clipper.caption_system.generate_srt_file(
            simple_captions, test_srt_path, 20
        )
        
        if success:
            print(f"✅ SRT generation successful: {test_srt_path}")
            print("🎯 SRT INTEGRATION WORKING!")
            
            # Show SRT preview
            with open(test_srt_path, 'r') as f:
                content = f.read()
                print("\\n📄 SRT Preview:")
                print(content[:200] + "..." if len(content) > 200 else content)
        else:
            print("❌ SRT generation failed")
    else:
        print("❌ Simple transcription failed")

def main():
    """Test the integrated SRT caption system"""
    print("🎯 AUTO-PEAK VIRAL CLIPPER - SRT CAPTION INTEGRATION")
    print("=" * 80)
    
    # Test integration first
    test_srt_integration()
    
    print("\\n📝 SRT INTEGRATION STEPS:")
    print("1. ✅ SRT caption system created")
    print("2. ✅ Auto-peak clipper updated for SRT")
    print("3. ✅ SRT caption burning implemented")
    print("4. 🔄 Next: Update Flask app to use SRT system")
    
    print("\\n🚀 TO UPDATE FLASK APP:")
    print("1. Import: from auto_peak_viral_clipper_srt import AutoPeakViralClipperSRT")
    print("2. Replace: clipper = AutoPeakViralClipperSimple() -> AutoPeakViralClipperSRT()")
    print("3. Use: clipper.update_captions_srt() in update_captions endpoint")
    
    print("\\n🎯 SRT ADVANTAGES:")
    print("✅ More reliable caption display")
    print("✅ Better FFmpeg compatibility")
    print("✅ Simpler format")
    print("✅ No ASS formatting issues")

if __name__ == "__main__":
    main()
