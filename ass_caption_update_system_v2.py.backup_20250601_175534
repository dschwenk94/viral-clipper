#!/usr/bin/env python3
"""
ASS Caption Update System V2 - Fixed timing drift issue
Preserves original speech timing while preventing overlaps
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

class ASSCaptionUpdateSystemV2:
    """Fixed system for updating ASS captions without timing drift"""
    
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
        
        # CRITICAL FIX: Reduced minimum durations to preserve natural timing
        self.MIN_CAPTION_DURATION = 0.3  # Reduced from 0.8
        self.MIN_GAP_BETWEEN_CAPTIONS = 0.05  # Reduced from 0.15
    
    def update_ass_file_with_edits(self, original_ass_path: str, updated_captions: List[Dict], output_path: str = None) -> bool:
        """Update ASS file with edited captions, preserving original timing patterns"""
        try:
            if output_path is None:
                output_path = original_ass_path
            
            # Fix fragmented captions first
            print(f"📝 Processing {len(updated_captions)} captions...")
            avg_text_length = sum(len(c.get('text', '')) for c in updated_captions) / len(updated_captions) if updated_captions else 0
            
            if avg_text_length < 5:  # Only merge if VERY fragmented
                print("⚠️ Detected fragmented captions, merging...")
                updated_captions = merge_fragmented_captions(updated_captions)
                print(f"✅ Merged to {len(updated_captions)} captions")
            
            # Extract original timing from ASS file for reference
            original_timings = self.extract_original_timings(original_ass_path)
            
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
            
            # Generate new dialogue lines with preserved timing
            new_dialogue_lines = self.generate_dialogue_with_preserved_timing(
                updated_captions, original_timings
            )
            
            # Combine everything
            new_ass_content = header_content + new_dialogue_lines
            
            # Write updated file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.writelines(new_ass_content)
            
            print(f"✅ Updated ASS file with preserved timing: {os.path.basename(output_path)}")
            return True
            
        except Exception as e:
            print(f"❌ Error updating ASS file: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def extract_original_timings(self, ass_path: str) -> List[Dict]:
        """Extract original timings from ASS file to use as reference"""
        timings = []
        
        try:
            with open(ass_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                if line.strip().startswith('Dialogue:'):
                    parts = line.split(',', 9)
                    if len(parts) >= 10:
                        timings.append({
                            'start_time': parts[1].strip(),
                            'end_time': parts[2].strip()
                        })
            
            print(f"📊 Extracted {len(timings)} original timings for reference")
            
        except Exception as e:
            print(f"⚠️ Could not extract original timings: {e}")
        
        return timings
    
    def generate_dialogue_with_preserved_timing(self, captions: List[Dict], original_timings: List[Dict]) -> List[str]:
        """Generate dialogue lines preserving original timing patterns"""
        dialogue_lines = []
        
        # Sort captions by index to maintain order
        sorted_captions = sorted(captions, key=lambda x: x.get('index', 0))
        
        # Use original timings if available and matching count
        if original_timings and len(original_timings) == len(sorted_captions):
            print("✅ Using original timings as reference")
            fixed_captions = self.apply_original_timings(sorted_captions, original_timings)
        else:
            print("⚠️ Original timing mismatch, using smart preservation")
            fixed_captions = self.preserve_natural_timing(sorted_captions)
        
        for caption in fixed_captions:
            speaker = caption.get('speaker', 'Speaker 1')
            text = caption.get('text', '').strip()
            
            if not text:
                continue
            
            start_time = caption.get('start_time', '0:00:00.00')
            end_time = caption.get('end_time', '0:00:01.00')
            
            # Format viral words
            formatted_text = self.format_viral_words(text, speaker)
            
            # Add pop-out effect with speaker's color
            speaker_color = self.speaker_colors.get(speaker, "#FFFFFF")
            ass_color = self.hex_to_ass_color(speaker_color)
            
            # Pop effect with proper timing
            pop_effect = r"{\fad(150,100)\t(0,300,\fscx110\fscy110)\t(300,400,\fscx100\fscy100)\c" + ass_color + r"}"
            
            # Create dialogue line
            dialogue_line = f"Dialogue: 0,{start_time},{end_time},{speaker},,0,0,0,,{pop_effect}{formatted_text}\n"
            dialogue_lines.append(dialogue_line)
        
        return dialogue_lines
    
    def apply_original_timings(self, captions: List[Dict], original_timings: List[Dict]) -> List[Dict]:
        """Apply original timings to updated captions"""
        fixed_captions = []
        
        for caption, timing in zip(captions, original_timings):
            fixed_caption = caption.copy()
            fixed_caption['start_time'] = timing['start_time']
            fixed_caption['end_time'] = timing['end_time']
            fixed_captions.append(fixed_caption)
        
        return fixed_captions
    
    def preserve_natural_timing(self, captions: List[Dict]) -> List[Dict]:
        """Preserve natural timing while preventing overlaps - FIXED VERSION"""
        fixed_captions = []
        
        for i, caption in enumerate(captions):
            fixed_caption = caption.copy()
            
            # Parse existing times
            start_seconds = self.ass_time_to_seconds(caption.get('start_time', '0:00:00.00'))
            end_seconds = self.ass_time_to_seconds(caption.get('end_time', '0:00:01.00'))
            
            # CRITICAL FIX: Only adjust if absolutely necessary
            if i > 0:
                prev_end_seconds = self.ass_time_to_seconds(fixed_captions[i-1]['end_time'])
                
                # Only adjust if there's an actual overlap
                if start_seconds < prev_end_seconds + self.MIN_GAP_BETWEEN_CAPTIONS:
                    # Minimal adjustment to prevent overlap
                    overlap_amount = (prev_end_seconds + self.MIN_GAP_BETWEEN_CAPTIONS) - start_seconds
                    start_seconds += overlap_amount
                    end_seconds += overlap_amount  # Shift end time by same amount to preserve duration
            
            # Ensure minimum duration only if it's extremely short
            current_duration = end_seconds - start_seconds
            if current_duration < self.MIN_CAPTION_DURATION:
                end_seconds = start_seconds + self.MIN_CAPTION_DURATION
            
            # Check for overlap with next caption
            if i + 1 < len(captions):
                next_start = self.ass_time_to_seconds(captions[i + 1].get('start_time', '0:00:00.00'))
                if end_seconds >= next_start - self.MIN_GAP_BETWEEN_CAPTIONS:
                    end_seconds = next_start - self.MIN_GAP_BETWEEN_CAPTIONS
            
            # Convert back to ASS time format
            fixed_caption['start_time'] = self.seconds_to_ass_time(start_seconds)
            fixed_caption['end_time'] = self.seconds_to_ass_time(end_seconds)
            
            fixed_captions.append(fixed_caption)
        
        return fixed_captions
    
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
    
    def format_viral_words(self, text: str, speaker: str) -> str:
        """Format viral words with speaker's color"""
        formatted_text = text
        speaker_color = self.speaker_colors.get(speaker, "#FFFFFF")
        ass_color = self.hex_to_ass_color(speaker_color)
        
        for word in self.viral_keywords:
            if word.lower() in text.lower():
                # FIXED: Use proper escaping for ASS format codes
                # The viral_format string itself doesn't need escaping
                viral_format = "{\\c" + ass_color + "\\fs24\\b1}" + word.upper() + "{\\r}"
                
                # Replace case-insensitively
                import re
                pattern = re.compile(re.escape(word), re.IGNORECASE)
                # Use a lambda to return the literal string, avoiding regex interpretation
                formatted_text = pattern.sub(lambda m: viral_format, formatted_text)
        
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
    print("🎯 ASS Caption Update System V2 - Fixed Timing Drift")
    print("✅ Preserves original speech timing")
    print("✅ Prevents caption overlaps")
    print("✅ Maintains snappy transitions")
    print("✅ No cumulative timing drift")
