#!/bin/bash
# Script to deploy anonymous support changes

echo "🚀 Deploying anonymous clip generation support..."

# Backup original multiuser files
echo "📦 Creating backups..."
cp app_multiuser.py app_multiuser_original.py 2>/dev/null || true
cp static/script_multiuser.js static/script_multiuser_original.js 2>/dev/null || true

# Deploy new anonymous versions
echo "📝 Updating files..."
cp app_multiuser_anonymous.py app_multiuser.py
cp static/script_multiuser_anonymous.js static/script_multiuser.js

# Run database migration
echo "🗄️ Running database migration..."
python migrations/002_anonymous_clips.py

echo "✅ Deployment complete!"
echo ""
echo "The app now supports:"
echo "- 🔓 Anonymous clip generation without sign-in"
echo "- 🔐 Authentication required only for YouTube upload"
echo "- 💾 Temporary storage of anonymous clips"
echo "- 🔄 Automatic conversion when users sign in"
echo ""
echo "Start the app with: python app_multiuser.py"
