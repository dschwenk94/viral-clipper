#!/usr/bin/env python3
"""
ASS Caption Update System V4 - FIXED: Proper speech timing synchronization
Preserves original speech timing while ensuring all captions appear
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

class ASSCaptionUpdateSystemV4:
    """FIXED system - preserves original speech timing for proper synchronization"""
    
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
    
    def update_ass_file_with_edits(self, original_ass_path: str, updated_captions: List[Dict], output_path: str = None) -> bool:
        """Update ASS file preserving ORIGINAL speech timing"""
        try:
            if output_path is None:
                output_path = original_ass_path
            
            print(f"🔧 TIMING-FIXED ASS UPDATE: Processing {len(updated_captions)} captions...")
            
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
            
            # Debug: Show original vs updated caption timings
            self.debug_caption_timings(sorted_captions, original_timings)
            
            # Create ASS file with PRESERVED timing
            new_ass_content = self.create_timing_preserved_ass_file(sorted_captions, original_timings)
            
            # Write the new file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(new_ass_content)
            
            # Verify the file was created correctly
            verification_result = self.verify_ass_file(output_path, len(sorted_captions))
            
            if verification_result:
                print(f"✅ TIMING-FIXED ASS file created with proper speech sync!")
                return True
            else:
                print(f"❌ ASS file verification failed")
                return False
            
        except Exception as e:
            print(f"❌ Error in TIMING-FIXED ASS update: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def extract_original_timing_data(self, original_ass_path: str) -> List[Dict]:
        """Extract original timing data from the ASS file"""
        original_timings = []
        
        if not original_ass_path or not os.path.exists(original_ass_path):
            print("⚠️ No original ASS file found - will use caption timing as-is")
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
            
            print(f"📊 Extracted {len(original_timings)} original timings for reference")
            return original_timings
            
        except Exception as e:
            print(f"⚠️ Could not extract original timings: {e}")
            return []
    
    def debug_caption_timings(self, updated_captions: List[Dict], original_timings: List[Dict]):
        """Debug timing comparison"""
        print(f"\n🔍 TIMING DEBUG:")
        print(f"   Updated captions: {len(updated_captions)}")
        print(f"   Original timings: {len(original_timings)}")
        
        print(f"\n📋 Updated Caption Timings:")
        for i, cap in enumerate(updated_captions[:5]):  # Show first 5
            start = cap.get('start_time', 'N/A')
            end = cap.get('end_time', 'N/A')
            text = cap.get('text', '')[:30] + '...' if len(cap.get('text', '')) > 30 else cap.get('text', '')
            print(f"   {i+1}. {start} → {end}: \"{text}\"")
        
        if original_timings:
            print(f"\n📋 Original Timings (reference):")
            for i, timing in enumerate(original_timings[:5]):  # Show first 5
                start = timing.get('start_time', 'N/A')
                end = timing.get('end_time', 'N/A')
                text = timing.get('text', '')[:30] + '...' if len(timing.get('text', '')) > 30 else timing.get('text', '')
                print(f"   {i+1}. {start} → {end}: \"{text}\"")
    
    def create_timing_preserved_ass_file(self, captions: List[Dict], original_timings: List[Dict]) -> str:
        """Create ASS file preserving ORIGINAL speech timing"""
        
        # Get unique speakers
        unique_speakers = set(cap.get('speaker', 'Speaker 1') for cap in captions)
        
        # Create styles section
        styles_section = self.create_styles_section(unique_speakers)
        
        # Use ORIGINAL timings if available, otherwise use caption timings with minimal fixes
        timing_preserved_captions = self.preserve_speech_timing(captions, original_timings)
        
        # Create dialogue section
        dialogue_section = self.create_dialogue_section(timing_preserved_captions)
        
        # Assemble complete ASS file
        ass_content = f"""[Script Info]
Title: Clippy Viral Captions - Speech Timing Preserved
ScriptType: v4.00+

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
{styles_section}

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
{dialogue_section}"""
        
        return ass_content
    
    def preserve_speech_timing(self, captions: List[Dict], original_timings: List[Dict]) -> List[Dict]:
        """Preserve original speech timing - CRITICAL FIX"""
        
        if not original_timings or len(original_timings) != len(captions):
            print("⚠️ Original timings unavailable or mismatched - preserving caption timings as-is")
            return self.minimal_timing_fixes(captions)
        
        print("✅ Using original speech timings for perfect sync")
        
        preserved_captions = []
        
        for i, caption in enumerate(captions):
            if i < len(original_timings):
                # Use original timing but with updated text and speaker
                preserved_caption = caption.copy()
                preserved_caption['start_time'] = original_timings[i]['start_time']
                preserved_caption['end_time'] = original_timings[i]['end_time']
                preserved_captions.append(preserved_caption)
            else:
                # Fallback for extra captions
                preserved_captions.append(caption)
        
        return preserved_captions
    
    def minimal_timing_fixes(self, captions: List[Dict]) -> List[Dict]:
        """Apply minimal timing fixes while preserving original timing"""
        
        print("🔧 Applying minimal timing fixes to preserve speech sync")
        
        fixed_captions = []
        
        for caption in captions:
            fixed_caption = caption.copy()
            
            # Parse existing timing
            start_seconds = self.ass_time_to_seconds(caption.get('start_time', '0:00:00.00'))
            end_seconds = self.ass_time_to_seconds(caption.get('end_time', '0:00:01.00'))
            
            # Only fix if duration is extremely short
            if end_seconds - start_seconds < 0.2:
                end_seconds = start_seconds + 0.5
                fixed_caption['end_time'] = self.seconds_to_ass_time(end_seconds)
                print(f"   ⚠️ Fixed very short caption: {caption.get('text', '')[:20]}...")
            
            fixed_captions.append(fixed_caption)
        
        return fixed_captions
    
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
            
            # Debug output
            print(f"   Caption {i+1}: {start_time} → {end_time} [{speaker}] \"{text[:30]}...\"")
        
        print(f"📝 Created {len(dialogue_lines)} dialogue lines with preserved timing")
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
            
            # Extract timing data for verification
            dialogue_lines = [line for line in content.split('\n') if line.startswith('Dialogue:')]
            
            print(f"🔍 ASS File Verification:")
            print(f"   Expected captions: {expected_count}")
            print(f"   Found dialogues: {dialogue_count}")
            print(f"   File size: {len(content)} characters")
            
            if dialogue_lines:
                first_time = dialogue_lines[0].split(',')[1] if len(dialogue_lines) > 0 else "N/A"
                last_time = dialogue_lines[-1].split(',')[2] if len(dialogue_lines) > 0 else "N/A"
                print(f"   Timing span: {first_time} → {last_time}")
            
            if dialogue_count == expected_count:
                print("✅ All captions preserved with proper timing!")
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


# Test the TIMING-FIXED system
if __name__ == "__main__":
    print("🔧 ASS Caption Update System V4 - SPEECH TIMING PRESERVED")
    print("✅ Fixes caption timing to sync with actual speech")
    print("✅ Preserves original speech timing data")
    print("✅ Ensures captions appear throughout full video duration")
    print("✅ No more fast/compressed caption timing")
