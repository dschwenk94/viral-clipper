#!/usr/bin/env python3
"""
Test script to verify the FIXED caption system works correctly
"""

import sys
import os
sys.path.append('/Users/davisschwenke/Clippy')

from ass_caption_update_system_v3 import ASSCaptionUpdateSystemV3

def test_caption_preservation():
    """Test that all captions are preserved in the ASS file"""
    
    print("🧪 Testing FIXED Caption System")
    print("=" * 50)
    
    # Create test captions (similar to what the frontend sends)
    test_captions = [
        {
            'index': 0,
            'text': 'you won that point,',
            'speaker': 'Speaker 2',
            'start_time': '0:00:00.00',
            'end_time': '0:00:01.59'
        },
        {
            'index': 1,
            'text': 'Steve.',
            'speaker': 'Speaker 2', 
            'start_time': '0:00:00.00',
            'end_time': '0:00:01.59'
        },
        {
            'index': 2,
            'text': 'Okay.',
            'speaker': 'Speaker 1',
            'start_time': '0:00:00.00',
            'end_time': '0:00:01.00'
        }
    ]
    
    print(f"📝 Testing with {len(test_captions)} captions:")
    for i, cap in enumerate(test_captions):
        print(f"   {i+1}. [{cap['speaker']}] \"{cap['text']}\"")
    
    # Initialize the FIXED system
    caption_system = ASSCaptionUpdateSystemV3()
    
    # Create a test ASS file
    test_ass_path = '/tmp/test_captions.ass'
    
    print(f"\n🔧 Creating test ASS file: {test_ass_path}")
    
    # Use the fixed system to create the ASS file
    success = caption_system.update_ass_file_with_edits(
        None,  # No original file
        test_captions,
        test_ass_path
    )
    
    if success:
        print("✅ ASS file created successfully!")
        
        # Verify the content
        with open(test_ass_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        dialogue_count = content.count('Dialogue:')
        
        print(f"\n🔍 Verification Results:")
        print(f"   Expected captions: {len(test_captions)}")
        print(f"   Found dialogues: {dialogue_count}")
        print(f"   File size: {len(content)} characters")
        
        if dialogue_count == len(test_captions):
            print("🎉 SUCCESS! All captions preserved in ASS file!")
            
            print("\n📄 ASS File Content:")
            print("-" * 30)
            print(content)
            print("-" * 30)
            
            return True
        else:
            print(f"❌ FAILURE! Expected {len(test_captions)} captions, found {dialogue_count}")
            return False
    else:
        print("❌ Failed to create ASS file")
        return False

if __name__ == "__main__":
    success = test_caption_preservation()
    if success:
        print("\n🎉 FIXED Caption System is working correctly!")
        print("✅ All captions will now be preserved in video regeneration")
    else:
        print("\n❌ Caption system test failed")
        sys.exit(1)
