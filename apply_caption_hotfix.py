#!/usr/bin/env python3
"""
HOTFIX: Fix regex escape issue in ASS caption update system
Fixes the "bad escape \c at position 1" error
"""

import os
import shutil
from datetime import datetime

def apply_hotfix():
    """Apply hotfix for the regex escape issue"""
    print("🔧 APPLYING HOTFIX FOR CAPTION UPDATE ERROR")
    print("=" * 60)
    
    target_file = "ass_caption_update_system_v2.py"
    
    if not os.path.exists(target_file):
        print(f"❌ {target_file} not found!")
        print("Please run this script from the Clippy directory")
        return False
    
    # Backup the file
    backup_name = f"{target_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(target_file, backup_name)
    print(f"✅ Backed up to: {backup_name}")
    
    # Read the file
    with open(target_file, 'r') as f:
        content = f.read()
    
    # Check if already fixed
    if 'lambda m: viral_format' in content:
        print("✅ File already fixed!")
        return True
    
    # Apply the fix
    old_line = 'formatted_text = pattern.sub(viral_format, formatted_text)'
    new_line = 'formatted_text = pattern.sub(lambda m: viral_format, formatted_text)'
    
    if old_line in content:
        content = content.replace(old_line, new_line)
        print("✅ Applied lambda fix for regex substitution")
    
    # Also fix the viral_format line
    old_format = r'viral_format = r"{\c" + ass_color + r"\fs24\b1}" + word.upper() + r"{\r}"'
    new_format = r'viral_format = "{\\c" + ass_color + "\\fs24\\b1}" + word.upper() + "{\\r}"'
    
    if old_format in content:
        content = content.replace(old_format, new_format)
        print("✅ Fixed escape sequences in viral_format")
    
    # Write the fixed content
    with open(target_file, 'w') as f:
        f.write(content)
    
    print("\n✅ HOTFIX APPLIED SUCCESSFULLY!")
    print("🎯 Caption updates should now work properly")
    print("\nNote: If you still have issues, try:")
    print("1. Restart the Clippy app")
    print("2. Generate a new clip and test caption editing")
    
    return True

if __name__ == "__main__":
    apply_hotfix()
