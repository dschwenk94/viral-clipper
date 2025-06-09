#!/usr/bin/env python3
"""
ASS Caption Timing Fix - Preserves original timing while preventing overlaps
"""

import os
import re
from typing import List, Dict
from dataclasses import dataclass

class ASSCaptionTimingFix:
    """Fix for caption timing drift issue when updating captions"""
    
    def __init__(self):
        self.MIN_CAPTION_DURATION = 0.5  # Reduced from 0.8 to preserve timing
        self.MIN_GAP_BETWEEN_CAPTIONS = 0.05  # Reduced from 0.15 to preserve timing
        
    def preserve_original_timing(self, captions: List[Dict]) -> List[Dict]:
        """
        Preserve original timing as much as possible while preventing overlaps.
        This is the key fix - we maintain the original start times and only
        adjust end times when necessary to prevent overlap.
        """
        fixed_captions = []
        
        for i, caption in enumerate(captions):
            fixed_caption = caption.copy()
            
            # Parse time strings to seconds
            start_seconds = self.ass_time_to_seconds(caption.get('start_time', '0:00:00.00'))
            end_seconds = self.ass_time_to_seconds(caption.get('end_time', '0:00:01.00'))
            
            # Only enforce minimum duration if it's too short
            current_duration = end_seconds - start_seconds
            if current_duration < self.MIN_CAPTION_DURATION:
                # Extend end time, but check if it would overlap with next caption
                proposed_end = start_seconds + self.MIN_CAPTION_DURATION
                
                # Check if there's a next caption
                if i + 1 < len(captions):
                    next_start = self.ass_time_to_seconds(captions[i + 1].get('start_time', '0:00:00.00'))
                    # Ensure we don't overlap with next caption
                    max_allowed_end = next_start - self.MIN_GAP_BETWEEN_CAPTIONS
                    end_seconds = min(proposed_end, max_allowed_end)
                else:
                    # Last caption, can extend freely
                    end_seconds = proposed_end
            
            # For all captions except the last, ensure no overlap with next
            if i + 1 < len(captions):
                next_start = self.ass_time_to_seconds(captions[i + 1].get('start_time', '0:00:00.00'))
                if end_seconds >= next_start - self.MIN_GAP_BETWEEN_CAPTIONS:
                    end_seconds = next_start - self.MIN_GAP_BETWEEN_CAPTIONS
            
            # Convert back to ASS time format
            fixed_caption['start_time'] = self.seconds_to_ass_time(start_seconds)
            fixed_caption['end_time'] = self.seconds_to_ass_time(end_seconds)
            
            fixed_captions.append(fixed_caption)
        
        return fixed_captions
    
    def distribute_captions_evenly(self, captions: List[Dict], total_duration: float = 30.0) -> List[Dict]:
        """
        Alternative approach: Distribute captions evenly across the video duration.
        This ensures consistent pacing and no drift.
        """
        if not captions:
            return []
        
        num_captions = len(captions)
        
        # Calculate time per caption including gaps
        time_per_caption = total_duration / num_captions
        caption_display_time = time_per_caption * 0.85  # 85% display, 15% gap
        gap_time = time_per_caption * 0.15
        
        distributed_captions = []
        
        for i, caption in enumerate(captions):
            distributed_caption = caption.copy()
            
            # Calculate evenly distributed timing
            start_time = i * time_per_caption
            end_time = start_time + caption_display_time
            
            # Convert to ASS time format
            distributed_caption['start_time'] = self.seconds_to_ass_time(start_time)
            distributed_caption['end_time'] = self.seconds_to_ass_time(end_time)
            
            distributed_captions.append(distributed_caption)
        
        return distributed_captions
    
    def smart_timing_adjustment(self, captions: List[Dict], original_captions: List[Dict] = None) -> List[Dict]:
        """
        Smart approach: Try to preserve original timing patterns while fixing overlaps.
        Uses the original caption timings as a reference if available.
        """
        if not captions:
            return []
        
        # If we have original captions, use their timing as reference
        if original_captions and len(original_captions) == len(captions):
            return self.preserve_timing_with_reference(captions, original_captions)
        
        # Otherwise, use the preserve original timing approach
        return self.preserve_original_timing(captions)
    
    def preserve_timing_with_reference(self, captions: List[Dict], original_captions: List[Dict]) -> List[Dict]:
        """
        Preserve timing using original captions as reference.
        This maintains the natural speech rhythm.
        """
        fixed_captions = []
        
        for i, (caption, original) in enumerate(zip(captions, original_captions)):
            fixed_caption = caption.copy()
            
            # Use original timing
            original_start = self.ass_time_to_seconds(original.get('start_time', '0:00:00.00'))
            original_end = self.ass_time_to_seconds(original.get('end_time', '0:00:01.00'))
            
            # Only adjust if there would be an overlap
            if i > 0:
                prev_end = self.ass_time_to_seconds(fixed_captions[i-1]['end_time'])
                if original_start <= prev_end + self.MIN_GAP_BETWEEN_CAPTIONS:
                    # Slight adjustment to prevent overlap
                    original_start = prev_end + self.MIN_GAP_BETWEEN_CAPTIONS
                    # Also adjust end time to maintain duration
                    duration = original_end - self.ass_time_to_seconds(original.get('start_time', '0:00:00.00'))
                    original_end = original_start + duration
            
            # Convert back to ASS time format
            fixed_caption['start_time'] = self.seconds_to_ass_time(original_start)
            fixed_caption['end_time'] = self.seconds_to_ass_time(original_end)
            
            fixed_captions.append(fixed_caption)
        
        return fixed_captions
    
    def ass_time_to_seconds(self, ass_time: str) -> float:
        """Convert ASS time format to seconds"""
        try:
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


# Example usage and testing
if __name__ == "__main__":
    print("🔧 ASS Caption Timing Fix")
    print("✅ Preserves original timing")
    print("✅ Prevents overlaps")
    print("✅ Maintains natural speech rhythm")
    
    # Test with sample captions
    sample_captions = [
        {'index': 0, 'text': 'Hello world', 'speaker': 'Speaker 1', 'start_time': '0:00:00.00', 'end_time': '0:00:01.50'},
        {'index': 1, 'text': 'This is a test', 'speaker': 'Speaker 2', 'start_time': '0:00:01.60', 'end_time': '0:00:03.00'},
        {'index': 2, 'text': 'Of caption timing', 'speaker': 'Speaker 1', 'start_time': '0:00:03.10', 'end_time': '0:00:04.50'},
    ]
    
    fixer = ASSCaptionTimingFix()
    fixed = fixer.preserve_original_timing(sample_captions)
    
    print("\nOriginal vs Fixed:")
    for orig, fix in zip(sample_captions, fixed):
        print(f"  {orig['text'][:20]:20} | {orig['start_time']} - {orig['end_time']} → {fix['start_time']} - {fix['end_time']}")
