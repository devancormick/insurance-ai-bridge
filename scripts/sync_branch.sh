#!/bin/bash

# Sync Branch Script
# This script helps sync a feature branch with staging or main

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

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)

# Parse arguments
TARGET_BRANCH=${1:-staging}
STRATEGY=${2:-rebase}  # rebase or merge

# Validate target branch
VALID_TARGETS=("main" "staging" "develop")
if [[ ! " ${VALID_TARGETS[@]} " =~ " ${TARGET_BRANCH} " ]]; then
    print_error "Invalid target branch: $TARGET_BRANCH"
    echo "Valid targets: ${VALID_TARGETS[*]}"
    exit 1
fi

# Validate strategy
VALID_STRATEGIES=("rebase" "merge")
if [[ ! " ${VALID_STRATEGIES[@]} " =~ " ${STRATEGY} " ]]; then
    print_error "Invalid strategy: $STRATEGY"
    echo "Valid strategies: ${VALID_STRATEGIES[*]}"
    exit 1
fi

# Check if on protected branch
PROTECTED_BRANCHES=("main" "staging")
if [[ " ${PROTECTED_BRANCHES[@]} " =~ " ${CURRENT_BRANCH} " ]]; then
    if [ "$CURRENT_BRANCH" == "$TARGET_BRANCH" ]; then
        print_warning "You're already on $TARGET_BRANCH. Syncing from remote..."
        git pull origin "$TARGET_BRANCH" || print_error "Could not pull from origin"
        exit 0
    fi
    print_error "Cannot sync protected branch '$CURRENT_BRANCH' directly."
    exit 1
fi

print_info "Syncing branch '$CURRENT_BRANCH' with '$TARGET_BRANCH' using $STRATEGY strategy"
echo ""

# Fetch latest changes
print_info "Fetching latest changes from origin..."
git fetch origin

# Check if target branch exists locally
if ! git show-ref --verify --quiet refs/heads/"$TARGET_BRANCH"; then
    print_info "Target branch '$TARGET_BRANCH' doesn't exist locally. Creating from remote..."
    git checkout -b "$TARGET_BRANCH" "origin/$TARGET_BRANCH" 2>/dev/null || {
        print_error "Target branch '$TARGET_BRANCH' doesn't exist on remote either!"
        exit 1
    }
    git checkout "$CURRENT_BRANCH"
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    print_warning "You have uncommitted changes!"
    read -p "Do you want to stash them before syncing? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        print_info "Stashing uncommitted changes..."
        git stash push -m "Auto-stash before syncing with $TARGET_BRANCH"
        STASHED=true
    else
        print_error "Please commit or stash your changes before syncing."
        exit 1
    fi
else
    STASHED=false
fi

# Update target branch
print_info "Updating $TARGET_BRANCH from remote..."
git checkout "$TARGET_BRANCH" 2>/dev/null || {
    print_info "Creating local tracking branch for $TARGET_BRANCH..."
    git checkout -b "$TARGET_BRANCH" "origin/$TARGET_BRANCH"
}
git pull origin "$TARGET_BRANCH" || print_warning "Could not pull $TARGET_BRANCH from remote"

# Switch back to feature branch
print_info "Switching back to $CURRENT_BRANCH..."
git checkout "$CURRENT_BRANCH"

# Sync with target branch
if [ "$STRATEGY" == "rebase" ]; then
    print_info "Rebasing $CURRENT_BRANCH onto $TARGET_BRANCH..."
    git rebase "$TARGET_BRANCH" || {
        print_error "Rebase failed! Resolve conflicts and run: git rebase --continue"
        if [ "$STASHED" = true ]; then
            print_info "Restoring stashed changes..."
            git stash pop
        fi
        exit 1
    }
else
    print_info "Merging $TARGET_BRANCH into $CURRENT_BRANCH..."
    git merge "$TARGET_BRANCH" --no-edit || {
        print_error "Merge failed! Resolve conflicts and commit."
        if [ "$STASHED" = true ]; then
            print_info "Restoring stashed changes..."
            git stash pop
        fi
        exit 1
    }
fi

# Restore stashed changes if any
if [ "$STASHED" = true ]; then
    print_info "Restoring stashed changes..."
    git stash pop || print_warning "Could not restore stashed changes. Run 'git stash list' to see stashed changes."
fi

print_info "✓ Branch synced successfully!"
echo ""
print_info "Next steps:"
echo "  1. Review the changes"
echo "  2. Run tests: pytest (backend) and npm test (frontend)"
echo "  3. Push: git push origin $CURRENT_BRANCH"
if [ "$STRATEGY" == "rebase" ]; then
    echo "  4. If already pushed, force push: git push --force-with-lease origin $CURRENT_BRANCH"
fi
echo ""

