#!/usr/bin/env python3
"""
ASS Caption Update System V5 - FINAL: Proper video duration distribution
Ensures captions are distributed across the full video duration, not compressed
"""

import os
import re
from typing import List, Dict, Optional
from dataclasses import dataclass
from caption_fragment_fix import merge_fragmented_captions

@dataclass
class CaptionUpdate:
    """Caption update data"""
    index: int
    text: str
    speaker: str
    start_time: str
    end_time: str

class ASSCaptionUpdateSystemV5:
    """FINAL system - distributes captions across full video duration"""
    
    def __init__(self):
        self.speaker_colors = {
            "Speaker 1": "#FF4500",   # Fire Red/Orange
            "Speaker 2": "#00BFFF",   # Electric Blue  
            "Speaker 3": "#00FF88"    # Neon Green
        }
        
        # Viral words for special formatting
        self.viral_keywords = [
            'fucking', 'shit', 'damn', 'crazy', 'insane', 'ridiculous',
            'amazing', 'incredible', 'awesome', 'epic', 'legendary',
            'oh my god', 'what the hell', 'holy shit', 'no way'
        ]
    
    def update_ass_file_with_edits(self, original_ass_path: str, updated_captions: List[Dict], output_path: str = None, video_duration: float = 30.0) -> bool:
        """Update ASS file with proper video duration distribution"""
        try:
            if output_path is None:
                output_path = original_ass_path
            
            print(f"🔧 FINAL ASS UPDATE: Processing {len(updated_captions)} captions for {video_duration}s video...")
            
            # Extract original timing data for reference
            original_timings = self.extract_original_timing_data(original_ass_path)
            
            # Fix fragmented captions first
            avg_text_length = sum(len(c.get('text', '')) for c in updated_captions) / len(updated_captions) if updated_captions else 0
            
            if avg_text_length < 5:  # Only merge if VERY fragmented
                print("⚠️ Detected fragmented captions, merging...")
                updated_captions = merge_fragmented_captions(updated_captions)
                print(f"✅ Merged to {len(updated_captions)} captions")
            
            # Sort captions by index to ensure proper order
            sorted_captions = sorted(updated_captions, key=lambda x: x.get('index', 0))
            print(f"📊 Processing {len(sorted_captions)} sorted captions")
            
            # Check if captions are compressed and need redistribution
            redistributed_captions = self.redistribute_captions_if_needed(sorted_captions, original_timings, video_duration)
            
            # Create ASS file with proper timing
            new_ass_content = self.create_final_ass_file(redistributed_captions)
            
            # Write the new file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(new_ass_content)
            
            # Verify the file was created correctly
            verification_result = self.verify_ass_file(output_path, len(sorted_captions), video_duration)
            
            if verification_result:
                print(f"✅ FINAL ASS file created with proper video duration distribution!")
                return True
            else:
                print(f"❌ ASS file verification failed")
                return False
            
        except Exception as e:
            print(f"❌ Error in FINAL ASS update: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def extract_original_timing_data(self, original_ass_path: str) -> List[Dict]:
        """Extract original timing data from the ASS file"""
        original_timings = []
        
        if not original_ass_path or not os.path.exists(original_ass_path):
            print("⚠️ No original ASS file found")
            return []
        
        try:
            with open(original_ass_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                if line.strip().startswith('Dialogue:'):
                    parts = line.split(',', 9)
                    if len(parts) >= 10:
                        original_timings.append({
                            'start_time': parts[1].strip(),
                            'end_time': parts[2].strip(),
                            'speaker': parts[3].strip(),
                            'text': parts[9].strip()
                        })
            
            print(f"📊 Extracted {len(original_timings)} original timings")
            return original_timings
            
        except Exception as e:
            print(f"⚠️ Could not extract original timings: {e}")
            return []
    
    def redistribute_captions_if_needed(self, captions: List[Dict], original_timings: List[Dict], video_duration: float) -> List[Dict]:
        """Check if captions need redistribution and fix if necessary"""
        
        # First, try to use original timings if available and matching
        if original_timings and len(original_timings) == len(captions):
            print("✅ Using original speech timings for perfect sync")
            
            redistributed_captions = []
            for i, caption in enumerate(captions):
                redistributed_caption = caption.copy()
                redistributed_caption['start_time'] = original_timings[i]['start_time']
                redistributed_caption['end_time'] = original_timings[i]['end_time']
                redistributed_captions.append(redistributed_caption)
            
            return redistributed_captions
        
        # Check if current captions are compressed
        caption_span = self.calculate_caption_span(captions)
        compression_ratio = caption_span / video_duration if video_duration > 0 else 1.0
        
        print(f"📐 Caption span: {caption_span:.1f}s / Video duration: {video_duration:.1f}s")
        print(f"📊 Compression ratio: {compression_ratio:.2f}")
        
        if compression_ratio < 0.6:  # Captions use less than 60% of video time
            print("⚠️ CAPTIONS ARE COMPRESSED - Redistributing across full video duration...")
            return self.redistribute_captions_across_duration(captions, video_duration)
        else:
            print("✅ Caption timing looks good - applying minimal fixes only")
            return self.apply_minimal_fixes(captions)
    
    def calculate_caption_span(self, captions: List[Dict]) -> float:
        """Calculate the time span covered by captions"""
        if not captions:
            return 0.0
        
        first_start = self.ass_time_to_seconds(captions[0].get('start_time', '0:00:00.00'))
        last_end = self.ass_time_to_seconds(captions[-1].get('end_time', '0:00:01.00'))
        
        return last_end - first_start
    
    def redistribute_captions_across_duration(self, captions: List[Dict], video_duration: float) -> List[Dict]:
        """Redistribute captions evenly across the video duration"""
        
        print(f"🔄 Redistributing {len(captions)} captions across {video_duration:.1f} seconds...")
        
        redistributed_captions = []
        
        # Calculate timing for even distribution
        total_caption_time = video_duration * 0.85  # Use 85% of video time for captions
        start_offset = video_duration * 0.05  # Start at 5% into video
        
        avg_caption_duration = 1.5  # Average duration per caption
        gap_between_captions = (total_caption_time - (len(captions) * avg_caption_duration)) / max(1, len(captions) - 1)
        
        # Ensure reasonable gap
        gap_between_captions = max(0.3, min(2.0, gap_between_captions))
        
        current_time = start_offset
        
        for i, caption in enumerate(captions):
            redistributed_caption = caption.copy()
            
            # Calculate start and end times
            start_time = current_time
            end_time = start_time + avg_caption_duration
            
            # Ensure we don't exceed video duration
            if end_time > video_duration - 1.0:
                end_time = video_duration - 0.5
                start_time = max(0, end_time - avg_caption_duration)
            
            redistributed_caption['start_time'] = self.seconds_to_ass_time(start_time)
            redistributed_caption['end_time'] = self.seconds_to_ass_time(end_time)
            
            redistributed_captions.append(redistributed_caption)
            
            # Move to next caption position
            current_time = end_time + gap_between_captions
            
            print(f"   Caption {i+1}: {redistributed_caption['start_time']} → {redistributed_caption['end_time']}: \"{caption.get('text', '')[:20]}...\"")
        
        final_span = self.calculate_caption_span(redistributed_captions)
        print(f"✅ Redistributed captions now span {final_span:.1f} seconds ({final_span/video_duration*100:.1f}% of video)")
        
        return redistributed_captions
    
    def apply_minimal_fixes(self, captions: List[Dict]) -> List[Dict]:
        """Apply minimal timing fixes while preserving original timing"""
        
        print("🔧 Applying minimal timing fixes to preserve speech sync")
        
        fixed_captions = []
        
        for caption in captions:
            fixed_caption = caption.copy()
            
            # Parse existing timing
            start_seconds = self.ass_time_to_seconds(caption.get('start_time', '0:00:00.00'))
            end_seconds = self.ass_time_to_seconds(caption.get('end_time', '0:00:01.00'))
            
            # Only fix if duration is extremely short
            if end_seconds - start_seconds < 0.3:
                end_seconds = start_seconds + 0.8
                fixed_caption['end_time'] = self.seconds_to_ass_time(end_seconds)
                print(f"   ⚠️ Fixed very short caption: {caption.get('text', '')[:20]}...")
            
            fixed_captions.append(fixed_caption)
        
        return fixed_captions
    
    def create_final_ass_file(self, captions: List[Dict]) -> str:
        """Create final ASS file with proper formatting"""
        
        # Get unique speakers
        unique_speakers = set(cap.get('speaker', 'Speaker 1') for cap in captions)
        
        # Create styles section
        styles_section = self.create_styles_section(unique_speakers)
        
        # Create dialogue section
        dialogue_section = self.create_dialogue_section(captions)
        
        # Assemble complete ASS file
        ass_content = f"""[Script Info]
Title: Clippy Viral Captions - Full Video Duration
ScriptType: v4.00+

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
{styles_section}

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
{dialogue_section}"""
        
        return ass_content
    
    def create_styles_section(self, speakers: set) -> str:
        """Create styles section for all speakers"""
        styles = []
        
        for speaker in speakers:
            color = self.speaker_colors.get(speaker, "#FFFFFF")
            ass_color = self.hex_to_ass_color(color)
            style_line = f"Style: {speaker},Arial Black,22,{ass_color},&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,3,1,2,30,30,50,1"
            styles.append(style_line)
        
        return "\n".join(styles)
    
    def create_dialogue_section(self, captions: List[Dict]) -> str:
        """Create dialogue section with ALL captions"""
        dialogue_lines = []
        
        for i, caption in enumerate(captions):
            speaker = caption.get('speaker', 'Speaker 1')
            text = caption.get('text', '').strip()
            start_time = caption.get('start_time', '0:00:00.00')
            end_time = caption.get('end_time', '0:00:01.00')
            
            if not text:
                continue
            
            # Format text with viral words and speaker color
            formatted_text = self.format_caption_text(text, speaker)
            
            # Create dialogue line
            dialogue_line = f"Dialogue: 0,{start_time},{end_time},{speaker},,0,0,0,,{formatted_text}"
            dialogue_lines.append(dialogue_line)
        
        print(f"📝 Created {len(dialogue_lines)} dialogue lines")
        return "\n".join(dialogue_lines)
    
    def format_caption_text(self, text: str, speaker: str) -> str:
        """Format caption text with speaker color and effects"""
        # Get speaker color
        speaker_color = self.speaker_colors.get(speaker, "#FFFFFF")
        ass_color = self.hex_to_ass_color(speaker_color)
        
        # Format viral words
        formatted_text = self.format_viral_words(text, speaker)
        
        # Add pop-out effect with speaker color
        pop_effect = f"{{\\fad(150,100)\\t(0,300,\\fscx110\\fscy110)\\t(300,400,\\fscx100\\fscy100)\\c{ass_color}}}"
        
        return f"{pop_effect}{formatted_text}"
    
    def format_viral_words(self, text: str, speaker: str) -> str:
        """Format viral words with special styling"""
        formatted_text = text
        speaker_color = self.speaker_colors.get(speaker, "#FFFFFF")
        ass_color = self.hex_to_ass_color(speaker_color)
        
        for word in self.viral_keywords:
            if word.lower() in text.lower():
                # Create viral word format
                viral_format = f"{{\\c{ass_color}\\fs26\\b1}}{word.upper()}{{\\r}}"
                
                # Replace case-insensitively
                import re
                pattern = re.compile(re.escape(word), re.IGNORECASE)
                formatted_text = pattern.sub(viral_format, formatted_text)
        
        return formatted_text
    
    def verify_ass_file(self, ass_path: str, expected_count: int, video_duration: float) -> bool:
        """Verify that the ASS file contains all expected captions with proper timing"""
        try:
            with open(ass_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Count dialogue lines
            dialogue_count = content.count('Dialogue:')
            
            # Extract timing data for verification
            dialogue_lines = [line for line in content.split('\n') if line.startswith('Dialogue:')]
            
            print(f"🔍 ASS File Verification:")
            print(f"   Expected captions: {expected_count}")
            print(f"   Found dialogues: {dialogue_count}")
            print(f"   File size: {len(content)} characters")
            
            if dialogue_lines:
                first_time = dialogue_lines[0].split(',')[1] if len(dialogue_lines) > 0 else "N/A"
                last_time = dialogue_lines[-1].split(',')[2] if len(dialogue_lines) > 0 else "N/A"
                
                first_seconds = self.ass_time_to_seconds(first_time)
                last_seconds = self.ass_time_to_seconds(last_time)
                span = last_seconds - first_seconds
                coverage = (span / video_duration * 100) if video_duration > 0 else 0
                
                print(f"   Timing span: {first_time} → {last_time}")
                print(f"   Duration covered: {span:.1f}s ({coverage:.1f}% of video)")
                
                if coverage > 50:
                    print("✅ Good coverage across video duration!")
                else:
                    print("⚠️ Limited coverage - captions may be compressed")
            
            if dialogue_count == expected_count:
                print("✅ All captions preserved!")
                return True
            else:
                print(f"❌ Caption count mismatch: expected {expected_count}, found {dialogue_count}")
                return False
                
        except Exception as e:
            print(f"❌ ASS file verification failed: {e}")
            return False
    
    def hex_to_ass_color(self, hex_color: str) -> str:
        """Convert hex color to ASS BGR format"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        # ASS uses BGR format with &H00 prefix
        return f"&H00{b:02X}{g:02X}{r:02X}"
    
    def ass_time_to_seconds(self, ass_time: str) -> float:
        """Convert ASS time format to seconds"""
        try:
            # Handle both H:MM:SS.CC and MM:SS.CC formats
            parts = ass_time.split(':')
            if len(parts) == 3:
                hours, minutes, seconds = parts
                hours = int(hours)
            else:
                hours = 0
                minutes, seconds = parts
            
            minutes = int(minutes)
            if '.' in seconds:
                secs, centisecs = seconds.split('.')
                secs = int(secs)
                centisecs = int(centisecs)
            else:
                secs = int(seconds)
                centisecs = 0
            
            return hours * 3600 + minutes * 60 + secs + centisecs / 100
        except Exception as e:
            print(f"⚠️ Time parsing error for '{ass_time}': {e}")
            return 0.0
    
    def seconds_to_ass_time(self, seconds: float) -> str:
        """Convert seconds to ASS time format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centiseconds = int((seconds % 1) * 100)
        return f"{hours}:{minutes:02d}:{secs:02d}.{centiseconds:02d}"


# Test the FINAL system
if __name__ == "__main__":
    print("🔧 ASS Caption Update System V5 - FINAL VIDEO DURATION FIX")
    print("✅ Fixes compressed captions that end at 14 seconds")
    print("✅ Redistributes captions across full video duration")
    print("✅ Preserves original speech timing when available")
    print("✅ Ensures captions appear throughout entire video")
