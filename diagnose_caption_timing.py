#!/usr/bin/env python3
"""
Diagnostic script to check caption timing issues in existing files
"""

import sys
import os
sys.path.append('/Users/davisschwenke/Clippy')

def analyze_existing_captions():
    """Analyze existing caption files to understand timing issues"""
    
    print("🔍 CAPTION TIMING DIAGNOSTIC")
    print("=" * 50)
    
    clips_dir = '/Users/davisschwenke/Clippy/clips'
    
    if not os.path.exists(clips_dir):
        print(f"❌ Clips directory not found: {clips_dir}")
        return
    
    # Find ASS files
    ass_files = [f for f in os.listdir(clips_dir) if f.endswith('_captions.ass')]
    
    print(f"📁 Found {len(ass_files)} ASS caption files:")
    
    for ass_file in ass_files[:3]:  # Check first 3 files
        print(f"\n📄 Analyzing: {ass_file}")
        
        ass_path = os.path.join(clips_dir, ass_file)
        
        try:
            with open(ass_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract dialogue lines
            dialogue_lines = [line for line in content.split('\n') if line.startswith('Dialogue:')]
            
            print(f"   Total dialogues: {len(dialogue_lines)}")
            
            if dialogue_lines:
                print(f"   📊 Timing Analysis:")
                
                for i, line in enumerate(dialogue_lines[:5]):  # Show first 5
                    parts = line.split(',')
                    if len(parts) >= 10:
                        start_time = parts[1]
                        end_time = parts[2]
                        speaker = parts[3]
                        text = parts[9]
                        
                        # Clean up text
                        if '{' in text and '}' in text:
                            text = text.split('}')[-1]
                        text = text[:40] + '...' if len(text) > 40 else text
                        
                        print(f"      {i+1}. {start_time} → {end_time} [{speaker}]: \"{text}\"")
                
                if len(dialogue_lines) > 5:
                    print(f"      ... and {len(dialogue_lines) - 5} more captions")
                
                # Check timing span
                first_line = dialogue_lines[0].split(',')
                last_line = dialogue_lines[-1].split(',')
                
                first_start = first_line[1] if len(first_line) > 1 else "N/A"
                last_end = last_line[2] if len(last_line) > 2 else "N/A"
                
                print(f"   ⏱️ Timing Span: {first_start} → {last_end}")
                
                # Convert to seconds
                def time_to_seconds(time_str):
                    try:
                        parts = time_str.split(':')
                        if len(parts) == 3:
                            h, m, s = parts
                            return int(h) * 3600 + int(m) * 60 + float(s)
                        return 0.0
                    except:
                        return 0.0
                
                first_seconds = time_to_seconds(first_start)
                last_seconds = time_to_seconds(last_end)
                span = last_seconds - first_seconds
                
                print(f"   📐 Duration: {span:.1f} seconds")
                
                # Identify potential issues
                if span < 20:
                    print("   ⚠️ WARNING: Captions may be compressed to early part of video")
                elif span > 25:
                    print("   ✅ GOOD: Captions span most of the video duration")
                else:
                    print("   ✅ OK: Reasonable caption span")
                
                # Check for timing overlaps
                overlaps = 0
                for i in range(len(dialogue_lines) - 1):
                    current_line = dialogue_lines[i].split(',')
                    next_line = dialogue_lines[i + 1].split(',')
                    
                    if len(current_line) > 2 and len(next_line) > 1:
                        current_end = time_to_seconds(current_line[2])
                        next_start = time_to_seconds(next_line[1])
                        
                        if current_end > next_start:
                            overlaps += 1
                
                if overlaps > 0:
                    print(f"   ⚠️ WARNING: {overlaps} timing overlaps detected")
                else:
                    print("   ✅ No timing overlaps detected")
            
        except Exception as e:
            print(f"   ❌ Error analyzing {ass_file}: {e}")
    
    print(f"\n💡 RECOMMENDATIONS:")
    print(f"   1. If captions are compressed to first 14 seconds:")
    print(f"      → The TIMING-FIXED system should preserve original speech timing")
    print(f"   2. If you see timing overlaps:")
    print(f"      → The fixed system eliminates overlaps that cause FFmpeg issues")
    print(f"   3. Use the updated system (V4) for proper speech synchronization")

if __name__ == "__main__":
    analyze_existing_captions()
