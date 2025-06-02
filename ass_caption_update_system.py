#!/usr/bin/env python3
"""
ASS Caption Update System - Fixes overlapping and adds update functionality
"""

import os
import re
from typing import List, Dict
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

class ASSCaptionUpdateSystem:
    """System for updating ASS captions and fixing overlap issues"""
    
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
    
    def fix_caption_overlaps(self, phrases: List[Dict], duration: float = 30.0) -> List[Dict]:
        """Fix overlapping captions by ensuring proper timing gaps"""
        fixed_phrases = []
        
        # Minimum gap between captions (in seconds)
        MIN_GAP = 0.1
        
        for i, phrase in enumerate(phrases):
            fixed_phrase = phrase.copy()
            
            # Ensure captions don't overlap
            if i > 0:
                prev_end = fixed_phrases[i-1]['end_time']
                if phrase['start_time'] < prev_end + MIN_GAP:
                    fixed_phrase['start_time'] = prev_end + MIN_GAP
            
            # Ensure caption has minimum duration
            MIN_DURATION = 0.5
            if fixed_phrase['end_time'] - fixed_phrase['start_time'] < MIN_DURATION:
                fixed_phrase['end_time'] = fixed_phrase['start_time'] + MIN_DURATION
            
            # Ensure doesn't exceed video duration
            if fixed_phrase['end_time'] > duration:
                fixed_phrase['end_time'] = duration
            
            # For last caption, extend slightly
            if i == len(phrases) - 1:
                fixed_phrase['end_time'] = min(fixed_phrase['end_time'] + 0.5, duration)
            
            fixed_phrases.append(fixed_phrase)
        
        return fixed_phrases
    
    def update_ass_file_with_edits(self, original_ass_path: str, updated_captions: List[Dict], output_path: str = None) -> bool:
        """Update ASS file with edited captions, maintaining speaker colors and effects"""
        try:
            if output_path is None:
                output_path = original_ass_path
            
            # Fix fragmented captions first
            print(f"📝 Processing {len(updated_captions)} captions...")
            avg_text_length = sum(len(c.get('text', '')) for c in updated_captions) / len(updated_captions) if updated_captions else 0
            
            if avg_text_length < 5:  # Only merge if VERY fragmented (single letters/words)
                print("⚠️ Detected fragmented captions, merging...")
                updated_captions = merge_fragmented_captions(updated_captions)
                print(f"✅ Merged to {len(updated_captions)} captions")
            
            # Read original ASS file
            with open(original_ass_path, 'r', encoding='utf-8') as f:
                ass_lines = f.readlines()
            
            # Find where Events section starts
            events_start = -1
            for i, line in enumerate(ass_lines):
                if line.strip() == '[Events]':
                    events_start = i
                    break
            
            if events_start == -1:
                raise Exception("No [Events] section found in ASS file")
            
            # Keep header and styles
            header_content = ass_lines[:events_start + 2]  # Include [Events] and Format line
            
            # Update styles section to ensure all speakers have correct colors
            header_content = self.update_ass_styles(header_content, updated_captions)
            
            # Generate new dialogue lines with NO OVERLAPS
            new_dialogue_lines = self.generate_updated_dialogue_lines(updated_captions)
            
            # Combine everything
            new_ass_content = header_content + new_dialogue_lines
            
            # Write updated file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.writelines(new_ass_content)
            
            print(f"✅ Updated ASS file: {os.path.basename(output_path)}")
            return True
            
        except Exception as e:
            print(f"❌ Error updating ASS file: {e}")
            return False
    
    def update_ass_styles(self, header_lines: List[str], captions: List[Dict]) -> List[str]:
        """Update styles section to include all speakers with correct colors"""
        updated_lines = []
        styles_section = False
        existing_styles = set()
        
        # First pass - collect existing styles
        for line in header_lines:
            if line.strip().startswith('Style:'):
                style_name = line.split(',')[0].replace('Style:', '').strip()
                existing_styles.add(style_name)
        
        # Get unique speakers from captions
        unique_speakers = set(cap.get('speaker', 'Speaker 1') for cap in captions)
        
        # Second pass - update header
        for line in header_lines:
            if line.strip() == '[V4+ Styles]':
                styles_section = True
                updated_lines.append(line)
            elif styles_section and line.strip() == '':
                # Add any missing speaker styles before empty line
                for speaker in unique_speakers:
                    if speaker not in existing_styles:
                        color = self.speaker_colors.get(speaker, "#FFFFFF")
                        ass_color = self.hex_to_ass_color(color)
                        style_line = f"Style: {speaker},Arial Black,20,{ass_color},&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,3,1,2,30,30,50,1\n"
                        updated_lines.append(style_line)
                styles_section = False
                updated_lines.append(line)
            else:
                updated_lines.append(line)
        
        return updated_lines
    
    def generate_updated_dialogue_lines(self, captions: List[Dict]) -> List[str]:
        """Generate dialogue lines with proper timing and effects"""
        dialogue_lines = []
        
        # Sort captions by index to maintain order
        sorted_captions = sorted(captions, key=lambda x: x.get('index', 0))
        
        # Fix any overlaps
        fixed_captions = self.fix_caption_overlaps_from_web(sorted_captions)
        
        # Minimum gap between captions
        MIN_GAP = 0.1
        
        for i, caption in enumerate(fixed_captions):
            speaker = caption.get('speaker', 'Speaker 1')
            text = caption.get('text', '').strip()
            
            if not text:
                continue
            
            # Get timing
            start_time = caption.get('start_time', '0:00:00.00')
            end_time = caption.get('end_time', '0:00:01.00')
            
            # Convert to seconds for overlap checking
            start_seconds = self.ass_time_to_seconds(start_time)
            end_seconds = self.ass_time_to_seconds(end_time)
            
            # Ensure no overlap with next caption
            if i + 1 < len(fixed_captions):
                next_start = self.ass_time_to_seconds(fixed_captions[i + 1].get('start_time', '0:00:00.00'))
                if end_seconds >= next_start:
                    end_seconds = next_start - MIN_GAP
            
            # Convert back to ASS time
            start_time = self.seconds_to_ass_time(start_seconds)
            end_time = self.seconds_to_ass_time(end_seconds)
            
            # Format viral words
            formatted_text = self.format_viral_words(text, speaker)
            
            # Add pop-out effect with speaker's color
            speaker_color = self.speaker_colors.get(speaker, "#FFFFFF")
            ass_color = self.hex_to_ass_color(speaker_color)
            
            # Pop effect that uses speaker's color
            pop_effect = r"{\fad(150,100)\t(0,300,\fscx110\fscy110)\t(300,400,\fscx100\fscy100)\c" + ass_color + r"}"
            
            # Create dialogue line
            dialogue_line = f"Dialogue: 0,{start_time},{end_time},{speaker},,0,0,0,,{pop_effect}{formatted_text}\n"
            dialogue_lines.append(dialogue_line)
        
        return dialogue_lines
    
    def fix_caption_overlaps_from_web(self, captions: List[Dict]) -> List[Dict]:
        """Fix overlapping captions from web input"""
        fixed_captions = []
        
        for i, caption in enumerate(captions):
            fixed_caption = caption.copy()
            
            # Parse time strings to seconds
            start_seconds = self.ass_time_to_seconds(caption.get('start_time', '0:00:00.00'))
            end_seconds = self.ass_time_to_seconds(caption.get('end_time', '0:00:01.00'))
            
            # Ensure minimum duration
            MIN_DURATION = 0.8
            if end_seconds - start_seconds < MIN_DURATION:
                end_seconds = start_seconds + MIN_DURATION
            
            # Check for overlap with previous caption
            if i > 0:
                prev_end_seconds = self.ass_time_to_seconds(fixed_captions[i-1]['end_time'])
                if start_seconds <= prev_end_seconds:
                    # Add gap after previous caption
                    start_seconds = prev_end_seconds + 0.15  # 150ms gap
                    end_seconds = max(end_seconds, start_seconds + MIN_DURATION)
            
            # Convert back to ASS time format
            fixed_caption['start_time'] = self.seconds_to_ass_time(start_seconds)
            fixed_caption['end_time'] = self.seconds_to_ass_time(end_seconds)
            
            fixed_captions.append(fixed_caption)
        
        return fixed_captions
    
    def format_viral_words(self, text: str, speaker: str) -> str:
        """Format viral words with speaker's color"""
        formatted_text = text
        speaker_color = self.speaker_colors.get(speaker, "#FFFFFF")
        ass_color = self.hex_to_ass_color(speaker_color)
        
        for word in self.viral_keywords:
            if word.lower() in text.lower():
                # Use raw string to avoid escape issues
                viral_format = r"{\c" + ass_color + r"\fs24\b1}" + word.upper() + r"{\r}"
                
                # Replace case-insensitively
                import re
                pattern = re.compile(re.escape(word), re.IGNORECASE)
                formatted_text = pattern.sub(viral_format, formatted_text)
        
        return formatted_text
    
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
        except:
            return 0.0
    
    def seconds_to_ass_time(self, seconds: float) -> str:
        """Convert seconds to ASS time format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centiseconds = int((seconds % 1) * 100)
        return f"{hours}:{minutes:02d}:{secs:02d}.{centiseconds:02d}"


# Test the system
if __name__ == "__main__":
    print("🎯 ASS Caption Update System")
    print("✅ Fixes overlapping captions")
    print("✅ Updates text and speaker assignments")
    print("✅ Maintains speaker colors in pop-out effects")
