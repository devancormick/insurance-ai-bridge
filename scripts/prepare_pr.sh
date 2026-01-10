#!/bin/bash

# Prepare PR Script
# This script helps prepare a branch for creating a pull request

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

# Check if on protected branch
PROTECTED_BRANCHES=("main" "staging")
if [[ " ${PROTECTED_BRANCHES[@]} " =~ " ${CURRENT_BRANCH} " ]]; then
    print_error "Cannot create PR from protected branch '$CURRENT_BRANCH'."
    exit 1
fi

print_info "Preparing PR for branch: $CURRENT_BRANCH"
echo ""

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    print_warning "You have uncommitted changes!"
    git status --short
    read -p "Do you want to commit them now? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Please commit your changes manually, then run this script again."
        exit 1
    else
        print_error "Please commit or stash your changes before preparing PR."
        exit 1
    fi
fi

# Fetch latest changes
print_info "Fetching latest changes from remote..."
git fetch origin

# Determine target branch (default: staging)
TARGET_BRANCH="staging"
if [[ "$CURRENT_BRANCH" =~ ^hotfix/ ]]; then
    TARGET_BRANCH="main"
    print_info "Hotfix branch detected. Target branch: main"
fi

# Check if target branch exists on remote
if ! git ls-remote --heads origin "$TARGET_BRANCH" | grep -q "$TARGET_BRANCH"; then
    print_warning "Target branch '$TARGET_BRANCH' doesn't exist on remote. Using 'main' instead."
    TARGET_BRANCH="main"
fi

# Check if branch is up to date with remote
if git ls-remote --heads origin "$CURRENT_BRANCH" | grep -q "$CURRENT_BRANCH"; then
    LOCAL_COMMIT=$(git rev-parse HEAD)
    REMOTE_COMMIT=$(git rev-parse "origin/$CURRENT_BRANCH" 2>/dev/null || echo "")
    
    if [ -n "$REMOTE_COMMIT" ] && [ "$LOCAL_COMMIT" != "$REMOTE_COMMIT" ]; then
        print_warning "Local branch is not in sync with remote!"
        git log --oneline "$CURRENT_BRANCH".."origin/$CURRENT_BRANCH" 2>/dev/null || true
        git log --oneline "origin/$CURRENT_BRANCH".."$CURRENT_BRANCH" 2>/dev/null || true
        read -p "Do you want to push your changes first? (Y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            print_info "Pushing to remote..."
            git push origin "$CURRENT_BRANCH" || {
                print_error "Push failed!"
                exit 1
            }
        fi
    fi
else
    print_info "Branch doesn't exist on remote. You'll need to push it."
fi

# Sync with target branch
print_info "Checking if branch is up to date with $TARGET_BRANCH..."
git fetch origin "$TARGET_BRANCH" > /dev/null 2>&1 || true

BASE_COMMIT=$(git merge-base "$CURRENT_BRANCH" "origin/$TARGET_BRANCH" 2>/dev/null || git merge-base "$CURRENT_BRANCH" "$TARGET_BRANCH" 2>/dev/null || echo "")
TARGET_COMMIT=$(git rev-parse "origin/$TARGET_BRANCH" 2>/dev/null || git rev-parse "$TARGET_BRANCH" 2>/dev/null || echo "")

if [ -n "$BASE_COMMIT" ] && [ -n "$TARGET_COMMIT" ] && [ "$BASE_COMMIT" != "$TARGET_COMMIT" ]; then
    print_warning "Branch is not up to date with $TARGET_BRANCH!"
    print_info "New commits in $TARGET_BRANCH:"
    git log --oneline "$BASE_COMMIT".."$TARGET_COMMIT" 2>/dev/null | head -5 || true
    
    read -p "Do you want to sync with $TARGET_BRANCH now? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        print_info "Syncing with $TARGET_BRANCH..."
        ./scripts/sync_branch.sh "$TARGET_BRANCH" rebase || {
            print_error "Sync failed! Please resolve conflicts and try again."
            exit 1
        }
    fi
fi

# Run tests
echo ""
print_info "Running pre-PR checks..."
echo ""

# Backend tests
if [ -d "backend" ]; then
    print_info "Running backend tests..."
    cd backend
    if command -v pytest &> /dev/null; then
        pytest tests/ -v --tb=short || {
            print_warning "Backend tests failed or pytest not available."
            cd ..
            read -p "Continue anyway? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        }
    else
        print_warning "pytest not found. Skipping backend tests."
    fi
    cd - > /dev/null
fi

# Frontend tests
if [ -d "frontend" ]; then
    print_info "Running frontend tests..."
    cd frontend
    if [ -f "package.json" ] && grep -q '"test"' package.json; then
        npm test -- --passWithNoTests || {
            print_warning "Frontend tests failed."
            cd ..
            read -p "Continue anyway? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        }
    else
        print_warning "No test script found. Skipping frontend tests."
    fi
    cd - > /dev/null
fi

# Check commit messages
print_info "Checking commit messages..."
INVALID_COMMITS=0
for commit in $(git log "origin/$TARGET_BRANCH".."$CURRENT_BRANCH" --format="%H" 2>/dev/null || git log "$TARGET_BRANCH".."$CURRENT_BRANCH" --format="%H" 2>/dev/null || echo ""); do
    if [ -n "$commit" ]; then
        MSG=$(git log -1 --format="%s" "$commit")
        if [[ ! "$MSG" =~ ^(Merge|Revert|fixup!|squash!|\[.*\]\ .+:\ .+) ]]; then
            echo -e "${YELLOW}⚠️  Invalid commit message format: $MSG${NC}"
            INVALID_COMMITS=$((INVALID_COMMITS + 1))
        fi
    fi
done

if [ $INVALID_COMMITS -gt 0 ]; then
    print_warning "Found $INVALID_COMMITS commit(s) with invalid message format."
    print_info "Expected format: [COMPONENT] Action: Description"
fi

# Show summary
echo ""
print_info "✓ PR Preparation Summary"
echo ""
print_info "Branch: $CURRENT_BRANCH"
print_info "Target: $TARGET_BRANCH"
echo ""

# Count commits
COMMIT_COUNT=$(git log "origin/$TARGET_BRANCH".."$CURRENT_BRANCH" --oneline 2>/dev/null | wc -l || git log "$TARGET_BRANCH".."$CURRENT_BRANCH" --oneline 2>/dev/null | wc -l || echo "0")
print_info "Commits to be included: $COMMIT_COUNT"
echo ""

# Show recent commits
if [ "$COMMIT_COUNT" -gt 0 ]; then
    print_info "Recent commits:"
    git log "origin/$TARGET_BRANCH".."$CURRENT_BRANCH" --oneline --decorate 2>/dev/null | head -10 || git log "$TARGET_BRANCH".."$CURRENT_BRANCH" --oneline --decorate 2>/dev/null | head -10 || true
    echo ""
fi

# Generate PR URL suggestion
REPO_URL=$(git config --get remote.origin.url 2>/dev/null || echo "")
if [[ "$REPO_URL" =~ github\.com[:/](.+/.+)(\.git)?$ ]]; then
    REPO="${BASH_REMATCH[1]%.git}"
    PR_URL="https://github.com/$REPO/compare/$TARGET_BRANCH...$CURRENT_BRANCH?expand=1"
    print_info "Create PR: $PR_URL"
fi

echo ""
print_info "Next steps:"
echo "  1. Push branch (if not already pushed): git push -u origin $CURRENT_BRANCH"
echo "  2. Create PR from GitHub UI or use the URL above"
echo "  3. Fill out the PR template"
echo "  4. Ensure all CI checks pass"
echo "  5. Request reviews"
echo ""

