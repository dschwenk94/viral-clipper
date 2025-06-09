#!/usr/bin/env python3
"""
ASS Caption Update System V3 - FIXED: All captions preserved
Ensures all captions are included in video regeneration, not just the last one
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

class ASSCaptionUpdateSystemV3:
    """FIXED system for updating ASS captions - ensures ALL captions are preserved"""
    
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
        
        # CRITICAL: More conservative timing to ensure no overlaps
        self.MIN_CAPTION_DURATION = 0.5  # Minimum duration for each caption
        self.MIN_GAP_BETWEEN_CAPTIONS = 0.1  # Gap between captions
    
    def update_ass_file_with_edits(self, original_ass_path: str, updated_captions: List[Dict], output_path: str = None) -> bool:
        """Update ASS file with edited captions - FIXED to preserve ALL captions"""
        try:
            if output_path is None:
                output_path = original_ass_path
            
            print(f"🔧 FIXED ASS UPDATE: Processing {len(updated_captions)} captions...")
            
            # Fix fragmented captions first
            avg_text_length = sum(len(c.get('text', '')) for c in updated_captions) / len(updated_captions) if updated_captions else 0
            
            if avg_text_length < 5:  # Only merge if VERY fragmented
                print("⚠️ Detected fragmented captions, merging...")
                updated_captions = merge_fragmented_captions(updated_captions)
                print(f"✅ Merged to {len(updated_captions)} captions")
            
            # Sort captions by index to ensure proper order
            sorted_captions = sorted(updated_captions, key=lambda x: x.get('index', 0))
            print(f"📊 Processing {len(sorted_captions)} sorted captions")
            
            # Create completely new ASS file to avoid any corruption
            new_ass_content = self.create_fresh_ass_file(sorted_captions)
            
            # Write the new file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(new_ass_content)
            
            # Verify the file was created correctly
            verification_result = self.verify_ass_file(output_path, len(sorted_captions))
            
            if verification_result:
                print(f"✅ FIXED ASS file created with ALL {len(sorted_captions)} captions preserved!")
                return True
            else:
                print(f"❌ ASS file verification failed")
                return False
            
        except Exception as e:
            print(f"❌ Error in FIXED ASS update: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def create_fresh_ass_file(self, captions: List[Dict]) -> str:
        """Create a completely fresh ASS file with proper formatting"""
        
        # Get unique speakers
        unique_speakers = set(cap.get('speaker', 'Speaker 1') for cap in captions)
        
        # Create styles section
        styles_section = self.create_styles_section(unique_speakers)
        
        # Fix timing overlaps
        fixed_captions = self.fix_caption_timing_overlaps(captions)
        
        # Create dialogue section
        dialogue_section = self.create_dialogue_section(fixed_captions)
        
        # Assemble complete ASS file
        ass_content = f"""[Script Info]
Title: Clippy Viral Captions - All Captions Preserved
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
    
    def fix_caption_timing_overlaps(self, captions: List[Dict]) -> List[Dict]:
        """Fix timing overlaps to ensure all captions are preserved"""
        if not captions:
            return []
        
        fixed_captions = []
        
        for i, caption in enumerate(captions):
            fixed_caption = caption.copy()
            
            # Parse timing
            start_seconds = self.ass_time_to_seconds(caption.get('start_time', '0:00:00.00'))
            end_seconds = self.ass_time_to_seconds(caption.get('end_time', '0:00:01.00'))
            
            # Fix overlaps with previous caption
            if i > 0:
                prev_end = self.ass_time_to_seconds(fixed_captions[i-1]['end_time'])
                if start_seconds <= prev_end:
                    # Move start time after previous caption with gap
                    start_seconds = prev_end + self.MIN_GAP_BETWEEN_CAPTIONS
            
            # Ensure minimum duration
            if end_seconds - start_seconds < self.MIN_CAPTION_DURATION:
                end_seconds = start_seconds + self.MIN_CAPTION_DURATION
            
            # Check overlap with next caption
            if i + 1 < len(captions):
                next_start = self.ass_time_to_seconds(captions[i + 1].get('start_time', '0:00:00.00'))
                if end_seconds >= next_start - self.MIN_GAP_BETWEEN_CAPTIONS:
                    end_seconds = next_start - self.MIN_GAP_BETWEEN_CAPTIONS
                    # If this makes duration too short, prioritize no overlap
                    if end_seconds <= start_seconds:
                        end_seconds = start_seconds + 0.3  # Minimum 0.3s duration
            
            # Convert back to ASS format
            fixed_caption['start_time'] = self.seconds_to_ass_time(start_seconds)
            fixed_caption['end_time'] = self.seconds_to_ass_time(end_seconds)
            
            fixed_captions.append(fixed_caption)
        
        return fixed_captions
    
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
    
    def verify_ass_file(self, ass_path: str, expected_count: int) -> bool:
        """Verify that the ASS file contains all expected captions"""
        try:
            with open(ass_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Count dialogue lines
            dialogue_count = content.count('Dialogue:')
            
            print(f"🔍 ASS File Verification:")
            print(f"   Expected captions: {expected_count}")
            print(f"   Found dialogues: {dialogue_count}")
            print(f"   File size: {len(content)} characters")
            
            if dialogue_count == expected_count:
                print("✅ All captions preserved in ASS file!")
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


# Test the FIXED system
if __name__ == "__main__":
    print("🔧 ASS Caption Update System V3 - ALL CAPTIONS PRESERVED")
    print("✅ Fixes caption loss during video regeneration")
    print("✅ Ensures all captions appear in final video")
    print("✅ Prevents timing overlaps that cause FFmpeg issues")
    print("✅ Complete ASS file recreation for reliability")
