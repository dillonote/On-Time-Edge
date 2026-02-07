#!/bin/bash

# On Time Edge Copy Bot v2.0 - Automated Setup Script (Mac/Linux)
# This script clones your repo, copies files, and pushes to GitHub

set -e  # Exit on any error

echo "=========================================="
echo "  On Time Edge Copy Bot v2.0 Setup"
echo "=========================================="
echo ""

# Configuration
REPO_URL="https://github.com/dillonote/On-Time-Edge.git"
REPO_NAME="On-Time-Edge"
WORK_DIR="$HOME/Desktop"
DOWNLOADS_DIR="$HOME/Downloads"

# Files to copy
FILES=(
    "main_enhanced.py"
    "ENHANCEMENTS.md"
    "MIGRATION.md"
    "BEFORE_AFTER.md"
    "test_suite.py"
    "README.md"
)

echo "📁 Working directory: $WORK_DIR"
echo "📥 Downloads directory: $DOWNLOADS_DIR"
echo ""

# Step 1: Navigate to work directory
echo "Step 1: Navigating to work directory..."
cd "$WORK_DIR"
echo "✅ In $WORK_DIR"
echo ""

# Step 2: Clone repo (or update if exists)
if [ -d "$REPO_NAME" ]; then
    echo "Step 2: Repository already exists, updating..."
    cd "$REPO_NAME"
    git pull
else
    echo "Step 2: Cloning repository..."
    git clone "$REPO_URL"
    cd "$REPO_NAME"
fi
echo "✅ Repository ready"
echo ""

# Step 3: Copy files from Downloads
echo "Step 3: Copying files from Downloads..."
MISSING_FILES=()

for file in "${FILES[@]}"; do
    if [ -f "$DOWNLOADS_DIR/$file" ]; then
        cp "$DOWNLOADS_DIR/$file" .
        echo "  ✅ Copied $file"
    else
        MISSING_FILES+=("$file")
        echo "  ⚠️  Missing $file"
    fi
done

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
    echo ""
    echo "❌ ERROR: Missing files in Downloads folder:"
    for file in "${MISSING_FILES[@]}"; do
        echo "  - $file"
    done
    echo ""
    echo "Please download these files first, then run this script again."
    exit 1
fi

echo "✅ All files copied"
echo ""

# Step 4: Check git status
echo "Step 4: Checking changes..."
git status
echo ""

# Step 5: Prompt for commit
read -p "Do you want to commit and push these changes? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Step 5: Committing changes..."
    git add .
    git commit -m "Add Sugarman v2.0 enhancements - trigger detection, variants, auto-objections, refinement"
    echo "✅ Changes committed"
    echo ""

    echo "Step 6: Pushing to GitHub..."
    git push origin main
    echo "✅ Pushed to GitHub"
    echo ""
else
    echo "⏭️  Skipping commit and push"
    echo ""
fi

# Step 7: Test installation (optional)
echo "=========================================="
echo "  Setup Complete!"
echo "=========================================="
echo ""
echo "Your repo is at: $WORK_DIR/$REPO_NAME"
echo "View on GitHub: https://github.com/dillonote/On-Time-Edge"
echo ""

read -p "Do you want to run the test suite now? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    echo ""
    echo "Running test suite..."
    python test_suite.py
else
    echo "To test later, run:"
    echo "  cd $WORK_DIR/$REPO_NAME"
    echo "  pip install -r requirements.txt"
    echo "  python test_suite.py"
fi

echo ""
echo "🎉 Done!"
