#!/bin/bash

# Setup Git Hooks Script
# This script installs git hooks from .githooks directory

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_error "This is not a git repository. Please run this script from the repository root."
    exit 1
fi

print_info "Setting up Git hooks..."
echo ""

# Get the git hooks directory
GIT_HOOKS_DIR=$(git rev-parse --git-dir)/hooks
SOURCE_HOOKS_DIR=".githooks"

# Check if .githooks directory exists
if [ ! -d "$SOURCE_HOOKS_DIR" ]; then
    print_error "Source hooks directory '$SOURCE_HOOKS_DIR' not found!"
    exit 1
fi

# Ensure git hooks directory exists
mkdir -p "$GIT_HOOKS_DIR"

# List of hooks to install
HOOKS=("pre-commit" "pre-push" "commit-msg")

# Install each hook
for hook in "${HOOKS[@]}"; do
    SOURCE_HOOK="$SOURCE_HOOKS_DIR/$hook"
    TARGET_HOOK="$GIT_HOOKS_DIR/$hook"
    
    if [ -f "$SOURCE_HOOK" ]; then
        # Backup existing hook if it exists and is different
        if [ -f "$TARGET_HOOK" ] && ! cmp -s "$SOURCE_HOOK" "$TARGET_HOOK"; then
            print_warning "Existing hook '$hook' found. Creating backup..."
            cp "$TARGET_HOOK" "$TARGET_HOOK.backup.$(date +%Y%m%d_%H%M%S)"
        fi
        
        # Copy hook and make it executable
        cp "$SOURCE_HOOK" "$TARGET_HOOK"
        chmod +x "$TARGET_HOOK"
        print_info "✓ Installed hook: $hook"
    else
        print_warning "Hook file '$SOURCE_HOOK' not found. Skipping..."
    fi
done

# Configure git to trust the hooks directory (if using Git 2.9+)
if git config --global core.hooksPath > /dev/null 2>&1; then
    CURRENT_HOOKS_PATH=$(git config --global core.hooksPath)
    if [ "$CURRENT_HOOKS_PATH" != "$GIT_HOOKS_DIR" ]; then
        print_warning "Git hooks path is set to: $CURRENT_HOOKS_PATH"
        print_info "Using local hooks instead."
    fi
fi

echo ""
print_info "Git hooks installed successfully!"
echo ""
print_info "Installed hooks:"
for hook in "${HOOKS[@]}"; do
    if [ -f "$GIT_HOOKS_DIR/$hook" ]; then
        echo "  ✓ $hook"
    fi
done

echo ""
print_warning "Note: If you want to use a different hooks location, you can configure it with:"
echo "  git config core.hooksPath .githooks"
echo ""

