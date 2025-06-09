#!/usr/bin/env python3
"""
Test script to verify the TIMING-FIXED caption system preserves speech timing
"""

import sys
import os
sys.path.append('/Users/davisschwenke/Clippy')

from ass_caption_update_system_v4 import ASSCaptionUpdateSystemV4

def test_timing_preservation():
    """Test that caption timing is properly preserved"""
    
    print("🧪 Testing TIMING-FIXED Caption System")
    print("=" * 50)
    
    # Create test captions with realistic timing (spread across 35 seconds)
    test_captions = [
        {
            'index': 0,
            'text': 'you won that point,',
            'speaker': 'Speaker 2',
            'start_time': '0:00:02.50',   # 2.5 seconds
            'end_time': '0:00:04.10'      # 4.1 seconds
        },
        {
            'index': 1,
            'text': 'Steve.',
            'speaker': 'Speaker 2', 
            'start_time': '0:00:15.20',   # 15.2 seconds  
            'end_time': '0:00:16.80'      # 16.8 seconds
        },
        {
            'index': 2,
            'text': 'Okay.',
            'speaker': 'Speaker 1',
            'start_time': '0:00:30.00',   # 30 seconds
            'end_time': '0:00:31.50'      # 31.5 seconds
        }
    ]
    
    print(f"📝 Testing with {len(test_captions)} captions with realistic timing:")
    for i, cap in enumerate(test_captions):
        print(f"   {i+1}. [{cap['speaker']}] {cap['start_time']} → {cap['end_time']}: \"{cap['text']}\"")
    
    # Initialize the TIMING-FIXED system
    caption_system = ASSCaptionUpdateSystemV4()
    
    # Create a test ASS file
    test_ass_path = '/tmp/test_timing_captions.ass'
    
    print(f"\n🔧 Creating timing-fixed ASS file: {test_ass_path}")
    
    # Use the timing-fixed system to create the ASS file
    success = caption_system.update_ass_file_with_edits(
        None,  # No original file
        test_captions,
        test_ass_path
    )
    
    if success:
        print("✅ ASS file created successfully!")
        
        # Verify the timing preservation
        with open(test_ass_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        dialogue_count = content.count('Dialogue:')
        
        print(f"\n🔍 Timing Verification Results:")
        print(f"   Expected captions: {len(test_captions)}")
        print(f"   Found dialogues: {dialogue_count}")
        
        # Extract and verify timing
        dialogue_lines = [line for line in content.split('\n') if line.startswith('Dialogue:')]
        
        print(f"\n📊 Caption Timing Analysis:")
        for i, line in enumerate(dialogue_lines):
            parts = line.split(',')
            if len(parts) >= 3:
                start_time = parts[1]
                end_time = parts[2]
                text = parts[-1] if len(parts) > 3 else ""
                # Clean up the text
                text = text.split('}')[-1] if '}' in text else text
                text = text[:30] + '...' if len(text) > 30 else text
                print(f"   {i+1}. {start_time} → {end_time}: \"{text}\"")
        
        # Check if timing spans the full duration
        if dialogue_lines:
            first_line = dialogue_lines[0].split(',')
            last_line = dialogue_lines[-1].split(',')
            
            first_start = first_line[1] if len(first_line) > 1 else "0:00:00.00"
            last_end = last_line[2] if len(last_line) > 2 else "0:00:00.00"
            
            print(f"\n⏱️ Timing Span:")
            print(f"   First caption starts: {first_start}")
            print(f"   Last caption ends: {last_end}")
            
            # Convert to seconds for analysis
            def time_to_seconds(time_str):
                parts = time_str.split(':')
                if len(parts) == 3:
                    h, m, s = parts
                    return int(h) * 3600 + int(m) * 60 + float(s)
                return 0.0
            
            first_seconds = time_to_seconds(first_start)
            last_seconds = time_to_seconds(last_end)
            total_span = last_seconds - first_seconds
            
            print(f"   Total span: {total_span:.1f} seconds")
            
            if total_span > 25:  # Should span most of a 35-second clip
                print("✅ EXCELLENT: Captions span full video duration!")
                return True
            else:
                print(f"⚠️ WARNING: Captions only span {total_span:.1f}s - may be compressed")
                return False
        
        print("\n📄 Complete ASS File:")
        print("-" * 50)
        print(content)
        print("-" * 50)
        
        return dialogue_count == len(test_captions)
    else:
        print("❌ Failed to create ASS file")
        return False

if __name__ == "__main__":
    success = test_timing_preservation()
    if success:
        print("\n🎉 TIMING-FIXED Caption System is working correctly!")
        print("✅ Captions will now sync properly with speech throughout the video")
    else:
        print("\n❌ Timing preservation test failed")
        sys.exit(1)
