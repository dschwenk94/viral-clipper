#!/bin/bash
# Git commands to create feature branch and preserve v1.x

echo "🌿 Creating feature branch for multi-user support..."

# Ensure we're on main and up to date
git checkout main
git pull origin main

# Create and tag v1.x branch to preserve single-user version
echo "📌 Creating v1.x branch to preserve single-user version..."
git checkout -b v1.x
git push origin v1.x
git tag v1.0.0 -m "Last single-user version before multi-user support"
git push origin v1.0.0

# Go back to main and create feature branch
echo "🔄 Creating feature branch..."
git checkout main
git checkout -b feature/multi-user-support

# Add all the safe files
echo "📝 Adding files to commit..."

# Add new multi-user files
git add app_multiuser.py
git add auth/
git add database/
git add migrations/
git add templates/index_multiuser.html
git add templates/auth_error.html
git add static/script_multiuser.js
git add setup_multiuser.py
git add MULTIUSER_README.md
git add .env.example

# Add updated files
git add README.md
git add CHANGELOG.md
git add requirements_webapp.txt
git add .gitignore

# Add any other Python files that were modified
git add auth/oauth_manager.py
git add create_tables.py
git add add_missing_columns.py
git add check_db.py
git add update_ytdlp.py

# Show what will be committed
echo "📋 Files to be committed:"
git status

echo ""
echo "⚠️  IMPORTANT: Before committing, please verify:"
echo "1. No .env file is included"
echo "2. No client_secrets.json is included"
echo "3. No token.pickle files are included"
echo ""
echo "If everything looks good, run:"
echo ""
echo "git commit -m \"feat: Add multi-user support with Google OAuth authentication"
echo ""
echo "- Implement per-user authentication with Google OAuth"
echo "- Add PostgreSQL database for user management"
echo "- Create separate YouTube upload credentials per user"
echo "- Add upload history tracking"
echo "- Implement secure session management"
echo "- Update UI for multi-user workflows"
echo ""
echo "BREAKING CHANGE: Default app is now multi-user version"
echo "See MULTIUSER_README.md for setup instructions\""
echo ""
echo "git push origin feature/multi-user-support"
