#!/usr/bin/env python3
"""Test script to diagnose Edit page issues"""

import os
import json
import sys
from pathlib import Path

# Add the Clippy directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def check_clips_directory():
    """Check if clips directory exists and list files"""
    clips_dir = Path(__file__).parent / 'clips'
    
    print("=== Checking Clips Directory ===")
    print(f"Clips directory: {clips_dir}")
    print(f"Exists: {clips_dir.exists()}")
    
    if clips_dir.exists():
        files = list(clips_dir.glob('*'))
        print(f"\nFound {len(files)} files:")
        for f in sorted(files):
            if f.is_file() and not f.name.startswith('.'):
                size = f.stat().st_size / 1024 / 1024  # MB
                print(f"  - {f.name} ({size:.2f} MB)")
    print()

def check_caption_files():
    """Check ASS caption files"""
    clips_dir = Path(__file__).parent / 'clips'
    
    print("=== Checking Caption Files ===")
    ass_files = list(clips_dir.glob('*.ass'))
    
    for ass_file in sorted(ass_files):
        print(f"\nChecking: {ass_file.name}")
        try:
            with open(ass_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            dialogue_count = sum(1 for line in lines if line.strip().startswith('Dialogue:'))
            print(f"  - Total lines: {len(lines)}")
            print(f"  - Dialogue lines: {dialogue_count}")
            
            # Show first few dialogue lines
            print("  - First few dialogues:")
            shown = 0
            for line in lines:
                if line.strip().startswith('Dialogue:') and shown < 3:
                    print(f"    {line.strip()[:80]}...")
                    shown += 1
        except Exception as e:
            print(f"  - Error reading file: {e}")
    print()

def test_clip_data_structure():
    """Test the expected clip data structure"""
    print("=== Expected Clip Data Structure ===")
    
    sample_clip_data = {
        'path': 'clips/auto_peak_clip__120s.mp4',
        'video_id': '',
        'original_title': 'Test Video',
        'optimal_timestamp': 120,
        'detection_confidence': 0.85,
        'duration': 30,
        'video_speakers': 2,
        'caption_speakers': 2,
        'speaker_switching': True,
        'phrase_segments': 15,
        'captions_added': True,
        'subtitle_file': 'clips/auto_peak_clip__120s_captions.ass',
        'file_size_mb': 5.2,
        'created_at': '2025-01-08T12:00:00',
        'auto_detected': True,
        'peak_signals': ['High engagement', 'Topic change'],
        'peak_reason': 'Viral moment detected',
        'captions': [
            {
                'text': 'Sample caption text',
                'speaker': 'Speaker 1',
                'start_time': '0:00:00.00',
                'end_time': '0:00:02.00',
                'index': 0
            }
        ]
    }
    
    print("Sample structure:")
    print(json.dumps(sample_clip_data, indent=2))
    print()

def test_video_serving():
    """Test if videos can be served"""
    print("=== Testing Video Serving ===")
    
    # Check if Flask app can be imported
    try:
        from app_multiuser import app
        print("✓ Flask app imported successfully")
        
        # Check if clips route exists
        rules = list(app.url_map.iter_rules())
        clips_route = next((r for r in rules if '/clips/' in str(r)), None)
        if clips_route:
            print(f"✓ Clips route found: {clips_route}")
        else:
            print("✗ Clips route not found")
            
    except ImportError as e:
        print(f"✗ Could not import Flask app: {e}")
    print()

def main():
    """Run all tests"""
    print("Clippy Edit Page Diagnostic Tool\n")
    
    check_clips_directory()
    check_caption_files()
    test_clip_data_structure()
    test_video_serving()
    
    print("\n=== Recommendations ===")
    print("1. Check browser console for JavaScript errors")
    print("2. Use browser Network tab to see if video requests are made")
    print("3. Check if video URLs are correctly formed (/clips/filename.mp4)")
    print("4. Verify clip_data is properly passed to the template")
    print("5. Use the debug endpoint: /api/debug/job/<job_id>")

if __name__ == "__main__":
    main()
