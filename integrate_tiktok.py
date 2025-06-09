#!/usr/bin/env python3
"""
Script to integrate TikTok routes into app_multiuser.py
"""

import re

# Read the TikTok routes
with open('/Users/davisschwenke/Clippy/tiktok_routes.py', 'r') as f:
    tiktok_routes = f.read()

# Read the current app file
with open('/Users/davisschwenke/Clippy/app_multiuser.py', 'r') as f:
    app_content = f.read()

# Extract just the imports and routes from tiktok_routes.py
imports_pattern = r'# Add these imports.*?from auth\.tiktok\.api_client import TikTokAPIClient'
routes_pattern = r'# Add these routes.*'

# Extract imports
imports_match = re.search(imports_pattern, tiktok_routes, re.DOTALL)
if imports_match:
    tiktok_imports = imports_match.group(0).replace('# Add these imports at the top of app_multiuser.py\n', '')
else:
    tiktok_imports = """from auth.multi_platform_oauth import multi_platform_oauth
from auth.tiktok.api_client import TikTokAPIClient"""

# Extract routes (everything after the imports section)
routes_start = tiktok_routes.find('# Add these routes after the existing auth routes')
if routes_start != -1:
    tiktok_routes_code = tiktok_routes[routes_start:].replace('# Add these routes after the existing auth routes\n\n', '')
else:
    print("Could not find routes marker")
    exit(1)

# Find where to insert imports (after the existing imports)
import_insert_pos = app_content.find('# Initialize Flask app')
if import_insert_pos == -1:
    print("Could not find import insertion point")
    exit(1)

# Insert imports
app_content = app_content[:import_insert_pos] + '\n# TikTok imports\n' + tiktok_imports + '\n\n' + app_content[import_insert_pos:]

# Find where to insert routes (after the back_to_input route)
route_insert_pos = app_content.find('# Cleanup task for expired anonymous clips')
if route_insert_pos == -1:
    print("Could not find route insertion point")
    exit(1)

# Insert routes
app_content = app_content[:route_insert_pos] + '\n# TikTok routes\n' + tiktok_routes_code + '\n\n' + app_content[route_insert_pos:]

# Write the updated app file
with open('/Users/davisschwenke/Clippy/app_multiuser_with_tiktok.py', 'w') as f:
    f.write(app_content)

print("✅ Created app_multiuser_with_tiktok.py with TikTok integration")
print("   Review the file and then rename it to app_multiuser.py")
