#!/usr/bin/env python3
"""
Test script to verify TikTok integration is complete
"""

import os
import sys
import importlib

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description}: {filepath} NOT FOUND")
        return False

def check_import(module_path, description):
    """Check if a module can be imported"""
    try:
        importlib.import_module(module_path)
        print(f"✓ {description}: {module_path}")
        return True
    except ImportError as e:
        print(f"✗ {description}: {module_path} - {e}")
        return False

def check_env_var(var_name):
    """Check if environment variable is set"""
    if os.getenv(var_name):
        print(f"✓ Environment variable: {var_name} is set")
        return True
    else:
        print(f"✗ Environment variable: {var_name} NOT SET")
        return False

def main():
    print("🎵 TikTok Integration Status Check\n")
    
    # Change to Clippy directory
    clippy_dir = "/Users/davisschwenke/Clippy"
    if os.path.exists(clippy_dir):
        os.chdir(clippy_dir)
        print(f"Working directory: {os.getcwd()}\n")
    
    all_checks_passed = True
    
    # Check backend files
    print("Backend Files:")
    all_checks_passed &= check_file_exists("app_multiuser_with_tiktok.py", "Main app with TikTok")
    all_checks_passed &= check_file_exists("tiktok_routes.py", "TikTok routes")
    all_checks_passed &= check_file_exists("auth/tiktok/__init__.py", "TikTok auth module")
    all_checks_passed &= check_file_exists("auth/tiktok/oauth_handler.py", "TikTok OAuth handler")
    all_checks_passed &= check_file_exists("auth/tiktok/api_client.py", "TikTok API client")
    all_checks_passed &= check_file_exists("auth/multi_platform_oauth.py", "Multi-platform OAuth")
    all_checks_passed &= check_file_exists("migrations/003_tiktok_support.py", "TikTok migration")
    
    print("\nFrontend Files:")
    all_checks_passed &= check_file_exists("static/script_multiuser_tiktok.js", "JavaScript with TikTok")
    all_checks_passed &= check_file_exists("templates/index_multiuser.html", "HTML template")
    all_checks_passed &= check_file_exists("static/style.css", "CSS with TikTok styles")
    
    print("\nDocumentation:")
    all_checks_passed &= check_file_exists("TIKTOK_SETUP.md", "TikTok setup guide")
    
    # Check imports
    print("\nModule Imports:")
    all_checks_passed &= check_import("auth.tiktok", "TikTok auth module")
    all_checks_passed &= check_import("auth.multi_platform_oauth", "Multi-platform OAuth")
    
    # Check environment variables
    print("\nEnvironment Variables:")
    env_check1 = check_env_var("TIKTOK_CLIENT_KEY")
    env_check2 = check_env_var("TIKTOK_CLIENT_SECRET")
    
    if not (env_check1 and env_check2):
        print("\n⚠️  TikTok credentials not set in environment")
        print("   Add to your .env file:")
        print("   TIKTOK_CLIENT_KEY=your_client_key_here")
        print("   TIKTOK_CLIENT_SECRET=your_client_secret_here")
    
    # Check database migration status
    print("\nDatabase Migration:")
    try:
        from database import get_db_connection
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if TikTok tables exist
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('platform_connections', 'tiktok_upload_history')
        """)
        
        tables = [row[0] for row in cur.fetchall()]
        
        if 'platform_connections' in tables:
            print("✓ Table 'platform_connections' exists")
        else:
            print("✗ Table 'platform_connections' NOT FOUND - run migration")
            all_checks_passed = False
            
        if 'tiktok_upload_history' in tables:
            print("✓ Table 'tiktok_upload_history' exists")
        else:
            print("✗ Table 'tiktok_upload_history' NOT FOUND - run migration")
            all_checks_passed = False
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"✗ Database check failed: {e}")
        all_checks_passed = False
    
    # Summary
    print("\n" + "="*50)
    if all_checks_passed and env_check1 and env_check2:
        print("✅ TikTok integration is COMPLETE!")
        print("\nNext steps:")
        print("1. Run the migration if needed: python migrations/003_tiktok_support.py")
        print("2. Start the app: python app_multiuser_with_tiktok.py")
        print("3. Connect your TikTok account from the UI")
    else:
        print("❌ TikTok integration is INCOMPLETE")
        print("\nPlease fix the issues above before proceeding")
    
    return 0 if all_checks_passed else 1

if __name__ == "__main__":
    sys.exit(main())
