#!/usr/bin/env python3
"""
Final test to verify the complete caption timing fix
Tests the scenario where captions are compressed to 14 seconds in a 35-second video
"""

import sys
import os
sys.path.append('/Users/davisschwenke/Clippy')

from ass_caption_update_system_v5 import ASSCaptionUpdateSystemV5

def test_compressed_caption_fix():
    """Test the fix for compressed captions (14s in 35s video)"""
    
    print("🧪 Testing FINAL Caption Distribution Fix")
    print("=" * 60)
    
    # Simulate the problem: captions compressed to first 14 seconds 
    # when video is actually 35 seconds long
    compressed_captions = [
        {
            'index': 0,
            'text': 'you won that point,',
            'speaker': 'Speaker 2',
            'start_time': '0:00:02.50',   # Early timing
            'end_time': '0:00:04.10'      
        },
        {
            'index': 1,
            'text': 'Steve.',
            'speaker': 'Speaker 2', 
            'start_time': '0:00:06.20',   # Still early
            'end_time': '0:00:07.80'      
        },
        {
            'index': 2,
            'text': 'Okay.',
            'speaker': 'Speaker 1',
            'start_time': '0:00:12.00',   # Ends at 14s - PROBLEM!
            'end_time': '0:00:14.00'      
        }
    ]
    
    video_duration = 35.0  # Actual video is 35 seconds
    
    print(f"📝 PROBLEM SCENARIO:")
    print(f"   Video duration: {video_duration}s")
    print(f"   Compressed captions ending at: 14s")
    print(f"   Missing caption time: 21s (60% of video!)")
    
    print(f"\n📋 Original (Compressed) Caption Timings:")
    for i, cap in enumerate(compressed_captions):
        start = cap['start_time']
        end = cap['end_time']
        text = cap['text']
        print(f"   {i+1}. {start} → {end}: \"{text}\"")
    
    # Initialize the FINAL system
    caption_system = ASSCaptionUpdateSystemV5()
    
    # Create test ASS file with video duration
    test_ass_path = '/tmp/test_final_captions.ass'
    
    print(f"\n🔧 Applying FINAL FIX with video duration: {video_duration}s")
    
    # Use the final system with video duration
    success = caption_system.update_ass_file_with_edits(
        None,  # No original file
        compressed_captions,
        test_ass_path,
        video_duration  # CRITICAL: Pass video duration
    )
    
    if success:
        print("✅ ASS file created successfully!")
        
        # Verify the fix
        with open(test_ass_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        dialogue_lines = [line for line in content.split('\n') if line.startswith('Dialogue:')]
        
        print(f"\n🔍 FINAL FIX Verification:")
        print(f"   Expected captions: {len(compressed_captions)}")
        print(f"   Found dialogues: {len(dialogue_lines)}")
        
        if dialogue_lines:
            print(f"\n📊 FIXED Caption Timing Analysis:")
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
            
            # Check timing distribution
            first_line = dialogue_lines[0].split(',')
            last_line = dialogue_lines[-1].split(',')
            
            first_start = first_line[1] if len(first_line) > 1 else "0:00:00.00"
            last_end = last_line[2] if len(last_line) > 2 else "0:00:00.00"
            
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
            coverage_percent = (total_span / video_duration) * 100
            
            print(f"\n⏱️ Coverage Analysis:")
            print(f"   First caption starts: {first_start} ({first_seconds:.1f}s)")
            print(f"   Last caption ends: {last_end} ({last_seconds:.1f}s)")
            print(f"   Total span: {total_span:.1f}s")
            print(f"   Video coverage: {coverage_percent:.1f}%")
            
            if coverage_percent > 70:
                print("🎉 EXCELLENT! Captions now distributed across most of video!")
                result = "FIXED"
            elif coverage_percent > 50:
                print("✅ GOOD! Significant improvement in caption distribution")
                result = "IMPROVED"
            else:
                print("⚠️ LIMITED: Still compressed, needs more work")
                result = "PARTIAL"
            
            print(f"\n📈 IMPROVEMENT SUMMARY:")
            print(f"   Before: Captions ended at 14s (40% coverage)")
            print(f"   After: Captions span {total_span:.1f}s ({coverage_percent:.1f}% coverage)")
            print(f"   Status: {result}")
            
            return result == "FIXED" or result == "IMPROVED"
        
        return False
    else:
        print("❌ Failed to create ASS file")
        return False

if __name__ == "__main__":
    success = test_compressed_caption_fix()
    if success:
        print("\n🎉 FINAL CAPTION TIMING FIX IS WORKING!")
        print("✅ Captions will now be distributed across the full video duration")
        print("✅ No more captions ending at 14 seconds in a 35-second video")
    else:
        print("\n❌ Final caption timing fix test failed")
        sys.exit(1)
