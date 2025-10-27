#!/bin/bash

# Git Helper Script for DProf Development
# Provides common Git operations with validation

echo "🔧 DProf Git Helper"
echo "=================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

# Function to create and checkout a new feature branch
new_feature() {
    if [ -z "$1" ]; then
        print_error "Please provide a feature name"
        echo "Usage: ./git_helper.sh feature my-feature-name"
        exit 1
    fi
    
    BRANCH_NAME="feature/$1"
    
    # Check if we're on main branch
    CURRENT_BRANCH=$(git branch --show-current)
    if [ "$CURRENT_BRANCH" != "main" ]; then
        print_warning "Not on main branch. Switching to main first..."
        git checkout main
    fi
    
    # Pull latest changes
    print_info "Pulling latest changes from main..."
    git pull origin main
    
    # Create and checkout new branch
    print_info "Creating feature branch: $BRANCH_NAME"
    git checkout -b "$BRANCH_NAME"
    
    print_success "Feature branch '$BRANCH_NAME' created and checked out"
}

# Function to create a hotfix branch
new_hotfix() {
    if [ -z "$1" ]; then
        print_error "Please provide a hotfix name"
        echo "Usage: ./git_helper.sh hotfix fix-critical-bug"
        exit 1
    fi
    
    BRANCH_NAME="hotfix/$1"
    
    # Check if we're on main branch
    CURRENT_BRANCH=$(git branch --show-current)
    if [ "$CURRENT_BRANCH" != "main" ]; then
        print_warning "Not on main branch. Switching to main first..."
        git checkout main
    fi
    
    # Pull latest changes
    print_info "Pulling latest changes from main..."
    git pull origin main
    
    # Create and checkout new branch
    print_info "Creating hotfix branch: $BRANCH_NAME"
    git checkout -b "$BRANCH_NAME"
    
    print_success "Hotfix branch '$BRANCH_NAME' created and checked out"
}

# Function to safely commit changes with validation
commit_changes() {
    # Check if there are changes to commit
    if git diff --quiet && git diff --staged --quiet; then
        print_warning "No changes to commit"
        exit 0
    fi
    
    # Show status
    print_info "Current git status:"
    git status --short
    echo
    
    # Check for common issues
    if git status --porcelain | grep -q "^??"; then
        print_warning "There are untracked files. Add them with 'git add' if needed."
    fi
    
    # Prompt for commit message if not provided
    if [ -z "$1" ]; then
        echo "Enter commit message:"
        read -r COMMIT_MSG
    else
        COMMIT_MSG="$1"
    fi
    
    if [ -z "$COMMIT_MSG" ]; then
        print_error "Commit message cannot be empty"
        exit 1
    fi
    
    # Add all staged changes
    git add .
    
    # Commit
    git commit -m "$COMMIT_MSG"
    
    print_success "Changes committed successfully"
}

# Function to prepare for pull request
prepare_pr() {
    CURRENT_BRANCH=$(git branch --show-current)
    
    if [ "$CURRENT_BRANCH" = "main" ]; then
        print_error "Cannot prepare PR from main branch"
        exit 1
    fi
    
    print_info "Preparing branch '$CURRENT_BRANCH' for pull request..."
    
    # Update main branch
    print_info "Updating main branch..."
    git checkout main
    git pull origin main
    
    # Return to feature branch
    git checkout "$CURRENT_BRANCH"
    
    # Rebase on main
    print_info "Rebasing on main..."
    if git rebase main; then
        print_success "Rebase successful"
    else
        print_error "Rebase conflicts detected. Resolve conflicts and run 'git rebase --continue'"
        exit 1
    fi
    
    # Push branch
    print_info "Pushing branch to origin..."
    git push -u origin "$CURRENT_BRANCH"
    
    print_success "Branch ready for pull request!"
    print_info "Create PR at: https://github.com/yourusername/dprof/compare/$CURRENT_BRANCH"
}

# Function to clean up merged branches
cleanup_branches() {
    print_info "Cleaning up merged branches..."
    
    # Switch to main
    git checkout main
    
    # Pull latest changes
    git pull origin main
    
    # Delete merged branches
    MERGED_BRANCHES=$(git branch --merged | grep -v "\*\|main\|master")
    
    if [ -z "$MERGED_BRANCHES" ]; then
        print_info "No merged branches to clean up"
    else
        echo "Merged branches to delete:"
        echo "$MERGED_BRANCHES"
        echo
        read -p "Delete these branches? (y/N): " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "$MERGED_BRANCHES" | xargs -n 1 git branch -d
            print_success "Merged branches deleted"
        else
            print_info "Branch cleanup cancelled"
        fi
    fi
}

# Function to show project status
status() {
    print_info "Repository Status"
    echo "================="
    echo
    
    # Current branch
    CURRENT_BRANCH=$(git branch --show-current)
    echo "Current branch: $CURRENT_BRANCH"
    
    # Commit count ahead/behind main
    if [ "$CURRENT_BRANCH" != "main" ]; then
        AHEAD=$(git rev-list --count HEAD ^main)
        BEHIND=$(git rev-list --count main ^HEAD)
        echo "Ahead of main: $AHEAD commits"
        echo "Behind main: $BEHIND commits"
    fi
    
    echo
    
    # Git status
    git status --short
    echo
    
    # Recent commits
    echo "Recent commits:"
    git log --oneline -5
}

# Main script logic
case "$1" in
    "feature")
        new_feature "$2"
        ;;
    "hotfix")
        new_hotfix "$2"
        ;;
    "commit")
        commit_changes "$2"
        ;;
    "pr"|"pull-request")
        prepare_pr
        ;;
    "cleanup")
        cleanup_branches
        ;;
    "status")
        status
        ;;
    *)
        echo "Usage: $0 {feature|hotfix|commit|pr|cleanup|status} [args]"
        echo
        echo "Commands:"
        echo "  feature <name>     Create and checkout a new feature branch"
        echo "  hotfix <name>      Create and checkout a new hotfix branch"
        echo "  commit [message]   Add and commit all changes"
        echo "  pr                 Prepare current branch for pull request"
        echo "  cleanup           Delete merged branches"
        echo "  status            Show repository status"
        echo
        echo "Examples:"
        echo "  $0 feature add-mysql-support"
        echo "  $0 commit 'Add new database connector'"
        echo "  $0 pr"
        exit 1
        ;;
esac