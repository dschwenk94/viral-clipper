#!/usr/bin/env python3
"""
Run TikTok migration from within the app context
"""

import os
import sys
sys.path.append('/Users/davisschwenke/Clippy')

# Load environment variables
from dotenv import load_dotenv
load_dotenv('/Users/davisschwenke/Clippy/.env')

# Import and run migration
from migrations.003_tiktok_support import run_migration

try:
    run_migration()
    print("✅ TikTok migration completed successfully!")
except Exception as e:
    print(f"❌ Migration failed: {e}")
