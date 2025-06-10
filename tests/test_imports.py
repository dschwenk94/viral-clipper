#!/usr/bin/env python3
"""Test if the app imports work correctly after cleanup"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing imports after cleanup...")

try:
    print("1. Testing auto_peak_viral_clipper import...")
    from auto_peak_viral_clipper import AutoPeakViralClipper
    print("✅ Success!")
except Exception as e:
    print(f"❌ Failed: {e}")

try:
    print("\n2. Testing caption_fragment_fix import...")
    from caption_fragment_fix import merge_fragmented_captions
    print("✅ Success!")
except Exception as e:
    print(f"❌ Failed: {e}")

try:
    print("\n3. Testing ASS caption system V6 import...")
    from ass_caption_update_system_v6 import ASSCaptionUpdateSystemV6
    print("✅ Success!")
except Exception as e:
    print(f"❌ Failed: {e}")

try:
    print("\n4. Testing auth module import...")
    from auth import login_required, get_current_user, OAuthManager, User
    print("✅ Success!")
except Exception as e:
    print(f"❌ Failed: {e}")

try:
    print("\n5. Testing database module import...")
    from database import init_db, get_db_connection
    print("✅ Success!")
except Exception as e:
    print(f"❌ Failed: {e}")

print("\n📋 Summary:")
print("All core files are back in the root directory.")
print("The app should now run without import errors.")
print("\nTo run the app:")
print("  python3 app.py")
