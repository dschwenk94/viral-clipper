#!/usr/bin/env python3
"""
Debug script for ASS caption update issues
"""

import os
import sys
from ass_caption_update_system_v2 import ASSCaptionUpdateSystemV2

def diagnose_caption_issue(subtitle_path: str):
    """Diagnose issues with caption files"""
    print("🔍 CAPTION UPDATE DIAGNOSTIC")
    print("=" * 60)
    
    # Check if file exists
    if not os.path.exists(subtitle_path):
        print(f"❌ Subtitle file not found: {subtitle_path}")
        return False
    
    print(f"✅ Subtitle file exists: {os.path.basename(subtitle_path)}")
    print(f"📊 File size: {os.path.getsize(subtitle_path)} bytes")
    
    # Try to read the file
    try:
        with open(subtitle_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"✅ File is readable")
        print(f"📄 Content length: {len(content)} characters")
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False
    
    # Check ASS file structure
    has_script_info = '[Script Info]' in content
    has_styles = '[V4+ Styles]' in content
    has_events = '[Events]' in content
    
    print(f"\n📋 ASS File Structure:")
    print(f"   [Script Info]: {'✅' if has_script_info else '❌'}")
    print(f"   [V4+ Styles]: {'✅' if has_styles else '❌'}")
    print(f"   [Events]: {'✅' if has_events else '❌'}")
    
    if not all([has_script_info, has_styles, has_events]):
        print(f"❌ Invalid ASS file structure")
        return False
    
    # Count dialogue lines
    dialogue_count = content.count('Dialogue:')
    print(f"\n📝 Dialogue lines: {dialogue_count}")
    
    # Try to extract captions
    try:
        updater = ASSCaptionUpdateSystemV2()
        timings = updater.extract_original_timings(subtitle_path)
        print(f"✅ Successfully extracted {len(timings)} timings")
    except Exception as e:
        print(f"❌ Error extracting timings: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Check for common issues
    print(f"\n🔧 Common Issues Check:")
    
    # Check for empty dialogue lines
    lines = content.split('\n')
    empty_dialogues = 0
    for line in lines:
        if line.startswith('Dialogue:') and line.count(',') >= 9:
            parts = line.split(',', 9)
            if len(parts) >= 10 and not parts[9].strip():
                empty_dialogues += 1
    
    if empty_dialogues > 0:
        print(f"   ⚠️ Found {empty_dialogues} empty dialogue lines")
    
    # Check for malformed timings
    malformed_timings = 0
    for line in lines:
        if line.startswith('Dialogue:'):
            parts = line.split(',', 9)
            if len(parts) >= 3:
                start_time = parts[1].strip()
                end_time = parts[2].strip()
                # Check format H:MM:SS.CC
                if not (len(start_time.split(':')) >= 2 and len(end_time.split(':')) >= 2):
                    malformed_timings += 1
    
    if malformed_timings > 0:
        print(f"   ⚠️ Found {malformed_timings} malformed timing entries")
    
    print(f"\n✅ Diagnostic complete")
    return True

def test_caption_update(subtitle_path: str):
    """Test updating captions with sample data"""
    print(f"\n🧪 Testing caption update...")
    
    # Create sample caption updates
    test_captions = [
        {
            'index': 0,
            'text': 'Test caption one',
            'speaker': 'Speaker 1',
            'start_time': '0:00:00.00',
            'end_time': '0:00:02.00'
        },
        {
            'index': 1,
            'text': 'Test caption two',
            'speaker': 'Speaker 2',
            'start_time': '0:00:02.10',
            'end_time': '0:00:04.00'
        }
    ]
    
    try:
        updater = ASSCaptionUpdateSystemV2()
        test_output = subtitle_path.replace('.ass', '_test_update.ass')
        
        success = updater.update_ass_file_with_edits(
            subtitle_path,
            test_captions,
            test_output
        )
        
        if success:
            print(f"✅ Test update successful!")
            print(f"📁 Test output: {os.path.basename(test_output)}")
            # Clean up test file
            if os.path.exists(test_output):
                os.remove(test_output)
        else:
            print(f"❌ Test update failed")
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        subtitle_file = sys.argv[1]
    else:
        # Try to find a recent ASS file in clips directory
        clips_dir = "clips"
        if os.path.exists(clips_dir):
            ass_files = [f for f in os.listdir(clips_dir) if f.endswith('.ass')]
            if ass_files:
                # Sort by modification time, newest first
                ass_files.sort(key=lambda x: os.path.getmtime(os.path.join(clips_dir, x)), reverse=True)
                subtitle_file = os.path.join(clips_dir, ass_files[0])
                print(f"🔍 Using most recent ASS file: {ass_files[0]}")
            else:
                print("❌ No ASS files found in clips directory")
                sys.exit(1)
        else:
            print("❌ Clips directory not found")
            sys.exit(1)
    
    diagnose_caption_issue(subtitle_file)
    test_caption_update(subtitle_file)
