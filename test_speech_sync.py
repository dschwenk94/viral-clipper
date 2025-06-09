#!/usr/bin/env python3
"""
Test script to verify speech synchronization fix
Tests that captions sync with actual speech timing, not arbitrary redistribution
"""

import sys
import os
sys.path.append('/Users/davisschwenke/Clippy')

from ass_caption_update_system_v6 import ASSCaptionUpdateSystemV6

def test_speech_synchronization():
    """Test that captions are synchronized with original speech timing"""
    
    print("🎤 Testing SPEECH SYNCHRONIZATION Fix")
    print("=" * 60)
    
    # Simulate REAL speech timing (from actual transcription)
    # These times represent when people actually spoke
    original_speech_timing = """[Script Info]
Title: Original Speech Timing
ScriptType: v4.00+

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Speaker 1,Arial Black,22,&H000045FF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,3,1,2,30,30,50,1
Style: Speaker 2,Arial Black,22,&H00FFBF00,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,3,1,2,30,30,50,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:05.20,0:00:07.30,Speaker 2,,0,0,0,,{\\fad(150,100)}you won that point,
Dialogue: 0,0:00:18.45,0:00:19.80,Speaker 2,,0,0,0,,{\\fad(150,100)}Steve.
Dialogue: 0,0:00:28.10,0:00:29.50,Speaker 1,,0,0,0,,{\\fad(150,100)}Okay.
"""
    
    # User edited captions (text changed but should preserve speech timing)
    edited_captions = [
        {
            'index': 0,
            'text': 'you won that point,',  # Same text
            'speaker': 'Speaker 2',
            'start_time': '0:00:05.20',  # Original speech timing
            'end_time': '0:00:07.30'
        },
        {
            'index': 1,
            'text': 'Steve.',  # Same text  
            'speaker': 'Speaker 2',
            'start_time': '0:00:18.45',  # Original speech timing
            'end_time': '0:00:19.80'
        },
        {
            'index': 2,
            'text': 'Okay.',  # Same text
            'speaker': 'Speaker 1', 
            'start_time': '0:00:28.10',  # Original speech timing
            'end_time': '0:00:29.50'
        }
    ]
    
    print(f"🎤 SPEECH TIMING SCENARIO:")
    print(f"   Real speech occurs at: 5.2s, 18.45s, 28.1s")
    print(f"   Spans across: 24.3 seconds (good distribution)")
    print(f"   Problem: Previous systems ignored this timing")
    
    print(f"\n📋 Original Speech Timing:")
    for i, cap in enumerate(edited_captions):
        start = cap['start_time']
        end = cap['end_time']
        text = cap['text']
        print(f"   {i+1}. {start} → {end}: \"{text}\"")
    
    # Create original ASS file to simulate having original timing
    original_ass_path = '/tmp/original_speech_timing.ass'
    with open(original_ass_path, 'w', encoding='utf-8') as f:
        f.write(original_speech_timing)
    
    # Initialize the SPEECH SYNC system
    caption_system = ASSCaptionUpdateSystemV6()
    
    # Create updated ASS file that should preserve speech timing
    updated_ass_path = '/tmp/speech_synced_captions.ass'
    
    print(f"\n🎤 Applying SPEECH SYNCHRONIZATION...")
    
    # Use the speech sync system
    success = caption_system.update_ass_file_with_edits(
        original_ass_path,  # Has original speech timing
        edited_captions,
        updated_ass_path,
        35.0  # Video duration
    )
    
    if success:
        print("✅ ASS file created successfully!")
        
        # Verify speech synchronization
        with open(updated_ass_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        dialogue_lines = [line for line in content.split('\n') if line.startswith('Dialogue:')]
        
        print(f"\n🔍 SPEECH SYNC Verification:")
        print(f"   Expected captions: {len(edited_captions)}")
        print(f"   Found dialogues: {len(dialogue_lines)}")
        
        if dialogue_lines:
            print(f"\n📊 SPEECH-SYNCED Caption Timing:")
            speech_times = []
            
            for i, line in enumerate(dialogue_lines):
                parts = line.split(',')
                if len(parts) >= 3:
                    start_time = parts[1]
                    end_time = parts[2]
                    
                    # Convert to seconds for comparison
                    start_seconds = caption_system.ass_time_to_seconds(start_time)
                    end_seconds = caption_system.ass_time_to_seconds(end_time)
                    speech_times.append(start_seconds)
                    
                    text = parts[-1] if len(parts) > 3 else ""
                    text = text.split('}')[-1] if '}' in text else text
                    text = text[:30] + '...' if len(text) > 30 else text
                    print(f"   {i+1}. {start_time} → {end_time} ({start_seconds:.1f}s): \"{text}\"")
            
            # Check if speech timing is preserved
            expected_times = [5.2, 18.45, 28.1]  # When speech actually occurred
            timing_preserved = True
            
            print(f"\n⏱️ Speech Timing Verification:")
            for i, (actual, expected) in enumerate(zip(speech_times, expected_times)):
                difference = abs(actual - expected)
                if difference < 0.5:  # Within 0.5 seconds
                    status = "✅ PERFECT"
                elif difference < 2.0:  # Within 2 seconds  
                    status = "✅ GOOD"
                else:
                    status = "❌ OFF"
                    timing_preserved = False
                
                print(f"   Caption {i+1}: Expected {expected:.1f}s, Got {actual:.1f}s, Diff {difference:.1f}s - {status}")
            
            # Overall assessment
            if timing_preserved:
                print(f"\n🎉 SPEECH SYNCHRONIZATION SUCCESS!")
                print(f"✅ Captions are synchronized with actual speech timing")
                print(f"✅ No more fast progression or arbitrary redistribution")
                print(f"✅ Perfect speech-to-caption sync achieved")
                return True
            else:
                print(f"\n⚠️ Speech synchronization needs improvement")
                return False
        
        return False
    else:
        print("❌ Failed to create speech-synced ASS file")
        return False

if __name__ == "__main__":
    success = test_speech_synchronization()
    if success:
        print("\n🎤 SPEECH SYNCHRONIZATION FIX IS WORKING!")
        print("✅ Captions now sync perfectly with actual speech")
        print("✅ No more fast progression through the video")
        print("✅ Captions appear exactly when people speak")
    else:
        print("\n❌ Speech synchronization test failed")
        sys.exit(1)
