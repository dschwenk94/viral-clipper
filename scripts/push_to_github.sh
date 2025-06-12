#!/bin/bash
# Complete Git push and release script for Clippy multi-user

echo "🚀 Pushing Clippy Multi-User Changes to GitHub"
echo "=============================================="

# Function to check if command succeeded
check_status() {
    if [ $? -eq 0 ]; then
        echo "✅ Success: $1"
    else
        echo "❌ Failed: $1"
        exit 1
    fi
}

# 1. Push the v1.x branch (preserving single-user version)
echo ""
echo "📌 Step 1: Pushing v1.x branch (single-user preservation)..."
git push origin v1.x
check_status "Pushed v1.x branch"

# 2. Push the feature branch
echo ""
echo "🌿 Step 2: Pushing feature/multi-user-support branch..."
git push origin feature/multi-user-support
check_status "Pushed feature branch"

# 3. Create a tag for v1.0.0 on the v1.x branch
echo ""
echo "🏷️  Step 3: Creating v1.0.0 tag for single-user version..."
git checkout v1.x
git tag -a v1.0.0 -m "Last stable single-user version before multi-user support"
git push origin v1.0.0
check_status "Created and pushed v1.0.0 tag"

# 4. Go back to feature branch
echo ""
echo "🔄 Step 4: Returning to feature branch..."
git checkout feature/multi-user-support
check_status "Switched to feature branch"

echo ""
echo "=============================================="
echo "✅ All branches and tags pushed successfully!"
echo ""
echo "📋 Next Steps:"
echo "1. Go to: https://github.com/dschwenk94/Clippy"
echo "2. You should see a banner to create a Pull Request"
echo "3. Click 'Compare & pull request' for feature/multi-user-support"
echo "4. Review the changes and merge when ready"
echo ""
echo "After merging:"
echo "1. git checkout main"
echo "2. git pull origin main" 
echo "3. git tag -a v2.0.0 -m 'Multi-user support release'"
echo "4. git push origin v2.0.0"
echo "5. Create a GitHub Release from the v2.0.0 tag"
echo ""
echo "🎉 Great work on the multi-user implementation!"
