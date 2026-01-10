#!/bin/bash

# Create Feature Branch Script
# This script helps create a feature branch following the naming convention

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

# Parse arguments
if [ $# -lt 2 ]; then
    print_error "Usage: $0 <ISSUE-NUMBER> <description> [branch-type]"
    echo ""
    echo "Examples:"
    echo "  $0 ISSUE-123 add-user-authentication"
    echo "  $0 ISSUE-456 fix-login-error bugfix"
    echo "  $0 ISSUE-789 security-patch hotfix"
    echo ""
    echo "Branch types: feature (default), bugfix, hotfix, docs, refactor"
    exit 1
fi

ISSUE_NUM=$1
DESCRIPTION=$2
BRANCH_TYPE=${3:-feature}

# Validate branch type
VALID_TYPES=("feature" "bugfix" "hotfix" "docs" "refactor")
if [[ ! " ${VALID_TYPES[@]} " =~ " ${BRANCH_TYPE} " ]]; then
    print_error "Invalid branch type: $BRANCH_TYPE"
    echo "Valid types: ${VALID_TYPES[*]}"
    exit 1
fi

# Format description (lowercase, replace spaces with hyphens, remove special chars)
FORMATTED_DESC=$(echo "$DESCRIPTION" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]/-/g' | sed 's/--*/-/g' | sed 's/^-\|-$//g')

# Create branch name
BRANCH_NAME="${BRANCH_TYPE}/${ISSUE_NUM}-${FORMATTED_DESC}"

print_info "Creating branch: $BRANCH_NAME"
echo ""

# Check current branch
CURRENT_BRANCH=$(git branch --show-current)
print_info "Current branch: $CURRENT_BRANCH"

# Ensure we're on main or staging
if [[ "$CURRENT_BRANCH" != "main" && "$CURRENT_BRANCH" != "staging" ]]; then
    print_warning "You're not on main or staging. Creating from current branch..."
    BASE_BRANCH="$CURRENT_BRANCH"
else
    BASE_BRANCH="$CURRENT_BRANCH"
fi

# Pull latest changes
print_info "Pulling latest changes from origin/$BASE_BRANCH..."
git pull origin "$BASE_BRANCH" || print_warning "Could not pull from origin. Make sure remote is configured."

# Check if branch already exists
if git show-ref --verify --quiet refs/heads/"$BRANCH_NAME"; then
    print_warning "Branch '$BRANCH_NAME' already exists locally!"
    read -p "Do you want to switch to it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git checkout "$BRANCH_NAME"
        print_info "Switched to existing branch: $BRANCH_NAME"
        exit 0
    else
        exit 1
    fi
fi

# Create and checkout new branch
print_info "Creating new branch from $BASE_BRANCH..."
git checkout -b "$BRANCH_NAME"

# Check if remote branch exists
if git ls-remote --heads origin "$BRANCH_NAME" | grep -q "$BRANCH_NAME"; then
    print_warning "Branch '$BRANCH_NAME' already exists on remote!"
    print_info "Tracking remote branch..."
    git branch --set-upstream-to=origin/"$BRANCH_NAME" "$BRANCH_NAME" || true
    git pull origin "$BRANCH_NAME" || true
else
    print_info "Branch created locally. Push to remote with:"
    echo "  git push -u origin $BRANCH_NAME"
fi

echo ""
print_info "✓ Branch '$BRANCH_NAME' is ready!"
echo ""
print_info "Next steps:"
echo "  1. Make your changes"
echo "  2. Commit with format: [COMPONENT] Action: Description (Closes #${ISSUE_NUM})"
echo "  3. Push: git push -u origin $BRANCH_NAME"
echo "  4. Create PR to staging branch"
echo ""

