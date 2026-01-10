#!/bin/bash

# Setup Git Workflow Script
# This script helps set up the Git workflow by creating the staging branch
# and verifying the repository setup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
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

print_info "Git Workflow Setup Script"
print_info "========================="
echo ""

# Check current branch
CURRENT_BRANCH=$(git branch --show-current)
print_info "Current branch: $CURRENT_BRANCH"

# Ensure we're on main branch
if [ "$CURRENT_BRANCH" != "main" ]; then
    print_warning "You're not on the main branch. Switching to main..."
    git checkout main
    CURRENT_BRANCH="main"
fi

# Pull latest changes
print_info "Pulling latest changes from origin/main..."
git pull origin main || print_warning "Could not pull from origin. Make sure remote is configured."

# Check if staging branch exists locally
if git show-ref --verify --quiet refs/heads/staging; then
    print_warning "Staging branch already exists locally."
    read -p "Do you want to recreate it from main? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Deleting local staging branch..."
        git branch -D staging
    else
        print_info "Keeping existing staging branch. Checking if it's up to date..."
        git checkout staging
        git merge main --no-edit || print_warning "Merge conflict or issue. Please resolve manually."
        git checkout main
        exit 0
    fi
fi

# Check if staging branch exists on remote
if git ls-remote --heads origin staging | grep -q staging; then
    print_warning "Staging branch already exists on remote."
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Fetching remote staging branch..."
        git fetch origin staging:staging 2>/dev/null || true
        git checkout staging
        git reset --hard main
        print_warning "Force pushing staging branch. This will overwrite remote staging!"
        read -p "Continue? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git push origin staging --force
        else
            print_info "Aborted. Staging branch was reset locally but not pushed."
            git checkout main
            exit 0
        fi
    else
        print_info "Fetching and checking out existing remote staging branch..."
        git fetch origin staging:staging
        git checkout staging
        git checkout main
        exit 0
    fi
else
    # Create new staging branch
    print_info "Creating new staging branch from main..."
    git checkout -b staging
    
    # Push staging branch to remote
    print_info "Pushing staging branch to origin..."
    git push -u origin staging
    
    print_info "Switching back to main branch..."
    git checkout main
fi

# Verify setup
echo ""
print_info "Verifying setup..."
echo ""

# Check branches
print_info "Local branches:"
git branch

echo ""
print_info "Remote branches:"
git branch -r | grep -E "(main|staging)" || print_warning "Could not verify remote branches."

# Check for required files
echo ""
print_info "Checking for required workflow files..."
REQUIRED_FILES=(
    ".github/workflows/ci.yml"
    ".github/BRANCH_PROTECTION_SETUP.md"
    "CONTRIBUTING.md"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_info "✅ Found: $file"
    else
        print_warning "⚠️  Missing: $file"
    fi
done

# Check for PR templates
if [ -d ".github" ]; then
    PR_TEMPLATES=(
        ".github/pull_request_template.md"
        ".github/PULL_REQUEST_TEMPLATE"
    )
    
    for template in "${PR_TEMPLATES[@]}"; do
        if [ -e "$template" ]; then
            print_info "✅ Found: $template"
        else
            print_warning "⚠️  Missing: $template"
        fi
    done
fi

echo ""
print_info "Setup complete!"
echo ""
print_warning "IMPORTANT: Next steps:"
echo "  1. Configure branch protection rules in GitHub UI"
echo "  2. Follow instructions in .github/BRANCH_PROTECTION_SETUP.md"
echo "  3. Ensure CI/CD workflows are working"
echo ""
print_info "To create a feature branch, use:"
echo "  ./scripts/create_feature_branch.sh ISSUE-123 description"
echo ""

