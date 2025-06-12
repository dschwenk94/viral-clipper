#!/usr/bin/env python3
"""
Setup script for Clippy multi-user mode
This script helps set up the PostgreSQL database and configuration
"""

import os
import sys
import secrets
import subprocess
from pathlib import Path

def check_postgresql():
    """Check if PostgreSQL is installed and running"""
    try:
        result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ PostgreSQL is installed:", result.stdout.strip())
            return True
        else:
            print("❌ PostgreSQL is not installed")
            return False
    except FileNotFoundError:
        print("❌ PostgreSQL is not installed")
        return False

def create_database():
    """Create the Clippy database"""
    print("\n📊 Creating PostgreSQL database...")
    
    # Get database credentials
    db_name = input("Database name (default: clippy): ").strip() or "clippy"
    db_user = input("Database user (default: clippy_user): ").strip() or "clippy_user"
    db_password = input("Database password (leave empty to generate): ").strip()
    
    if not db_password:
        db_password = secrets.token_urlsafe(32)
        print(f"Generated password: {db_password}")
    
    # Create database and user
    try:
        # Connect as postgres superuser
        print("\nCreating database and user...")
        commands = [
            f"CREATE USER {db_user} WITH PASSWORD '{db_password}';",
            f"CREATE DATABASE {db_name} OWNER {db_user};",
            f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user};"
        ]
        
        for cmd in commands:
            result = subprocess.run(
                ['psql', '-U', 'postgres', '-c', cmd],
                capture_output=True,
                text=True
            )
            if result.returncode != 0 and "already exists" not in result.stderr:
                print(f"Warning: {result.stderr}")
        
        print("✅ Database created successfully!")
        return db_name, db_user, db_password
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return None, None, None

def create_env_file(db_name, db_user, db_password):
    """Create .env file with configuration"""
    print("\n📝 Creating .env file...")
    
    env_content = f"""# Clippy Multi-User Environment Configuration

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME={db_name}
DB_USER={db_user}
DB_PASSWORD={db_password}

# Security Keys
SECRET_KEY={secrets.token_urlsafe(32)}
TOKEN_ENCRYPTION_KEY={secrets.token_urlsafe(32)}

# App Configuration
FLASK_ENV=development
FLASK_DEBUG=True
"""
    
    env_path = Path(".env")
    if env_path.exists():
        backup = input(".env file already exists. Backup existing? (y/n): ").lower()
        if backup == 'y':
            import time
            env_path.rename(f".env.backup_{int(time.time())}")
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("✅ .env file created successfully!")

def run_migrations():
    """Run database migrations"""
    print("\n🔄 Running database migrations...")
    
    try:
        # Run migration script
        result = subprocess.run(
            [sys.executable, "migrations/001_initial_setup.py"],
            capture_output=True,
            text=True,
            env={**os.environ}  # Pass current environment variables
        )
        
        if result.returncode == 0:
            print("✅ Database migrations completed!")
        else:
            print(f"❌ Migration failed: {result.stderr}")
            print(f"Output: {result.stdout}")
            
    except Exception as e:
        print(f"❌ Error running migrations: {e}")

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing dependencies...")
    
    try:
        # First install python-dotenv
        subprocess.run([
            sys.executable, "-m", "pip", "install", "python-dotenv"
        ], check=True)
        
        # Then install other requirements
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements_webapp.txt"
        ], check=True)
        
        print("✅ Dependencies installed successfully!")
        
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False
    
    return True

def main():
    """Main setup process"""
    print("🎯 Clippy Multi-User Setup")
    print("=" * 50)
    
    # Check prerequisites
    if not check_postgresql():
        print("\n⚠️  Please install PostgreSQL first:")
        print("  macOS: brew install postgresql")
        print("  Ubuntu: sudo apt install postgresql")
        print("  Windows: Download from https://www.postgresql.org/download/")
        return
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Failed to install dependencies. Please install manually.")
        return
    
    # Create database
    db_name, db_user, db_password = create_database()
    if not db_name:
        print("\n❌ Database setup failed. Please create manually.")
        return
    
    # Create .env file
    create_env_file(db_name, db_user, db_password)
    
    # Load the .env file for migrations
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️  Could not load .env file. Migrations may fail.")
    
    # Run migrations
    run_migrations()
    
    print("\n✅ Setup complete!")
    print("\n📋 Next steps:")
    print("1. Make sure your client_secrets.json file is in place")
    print("2. Run the app with: python app_multiuser.py")
    print("3. Sign in with Google when prompted")
    print("\n🔐 Important: Keep your .env file secure and never commit it to git!")

if __name__ == "__main__":
    main()
