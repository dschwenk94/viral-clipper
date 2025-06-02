#!/usr/bin/env python3
"""
Patch to fix caption timing drift issue in Clippy
Apply this to use the fixed ASS caption update system
"""

import os
import shutil
from datetime import datetime

def apply_timing_fix():
    """Apply the timing fix to the Clippy system"""
    
    print("🔧 Applying Caption Timing Fix...")
    print("=" * 60)
    
    # Backup original files
    backup_dir = f"backups/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    files_to_backup = [
        "ass_caption_update_system.py",
        "auto_peak_viral_clipper.py"
    ]
    
    for file in files_to_backup:
        if os.path.exists(file):
            shutil.copy2(file, os.path.join(backup_dir, file))
            print(f"✅ Backed up {file}")
    
    # Update auto_peak_viral_clipper.py to use the fixed system
    clipper_path = "auto_peak_viral_clipper.py"
    
    if os.path.exists(clipper_path):
        with open(clipper_path, 'r') as f:
            content = f.read()
        
        # Replace the import
        content = content.replace(
            "from ass_caption_update_system import ASSCaptionUpdateSystem",
            "from ass_caption_update_system_v2 import ASSCaptionUpdateSystemV2 as ASSCaptionUpdateSystem"
        )
        
        with open(clipper_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Updated {clipper_path} to use fixed caption system")
    
    # Also update app.py to use the fixed system
    app_path = "app.py"
    
    if os.path.exists(app_path):
        with open(app_path, 'r') as f:
            content = f.read()
        
        # Add import for the fixed system after the existing imports
        if "from ass_caption_update_system_v2 import" not in content:
            # Find where to insert the import
            import_location = content.find("from caption_fragment_fix import merge_fragmented_captions")
            if import_location != -1:
                # Insert after this import
                end_of_line = content.find("\n", import_location)
                content = (content[:end_of_line + 1] + 
                          "from ass_caption_update_system_v2 import ASSCaptionUpdateSystemV2\n" + 
                          content[end_of_line + 1:])
                
                print("✅ Added import for fixed caption system to app.py")
        
        with open(app_path, 'w') as f:
            f.write(content)
    
    print("\n📊 Summary of changes:")
    print("1. Reduced MIN_CAPTION_DURATION from 0.8s to 0.3s")
    print("2. Reduced MIN_GAP_BETWEEN_CAPTIONS from 0.15s to 0.05s")
    print("3. Added logic to preserve original timing patterns")
    print("4. Fixed cumulative timing drift issue")
    
    print("\n✅ Caption timing fix applied successfully!")
    print("🎯 Edited captions will now maintain proper sync")
    
    return True

if __name__ == "__main__":
    apply_timing_fix()
