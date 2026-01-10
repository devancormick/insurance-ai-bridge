# Branch Protection Rules Setup Guide

This document provides step-by-step instructions for setting up branch protection rules in the GitHub repository UI.

## Overview

Branch protection rules ensure code quality and prevent direct pushes to protected branches. We have two protected branches:
- **`main`** - Production branch (strictest protection)
- **`staging`** - Testing branch (moderate protection)

## Setting Up Branch Protection Rules

### Step 1: Navigate to Branch Protection Settings

1. Go to your GitHub repository
2. Click on **Settings**
3. In the left sidebar, click on **Branches** under "Code and automation"
4. Click **Add branch protection rule** or click on **Add rule**

### Step 2: Configure Main Branch Protection

#### Branch Name Pattern
- Enter `main` in the "Branch name pattern" field

#### Protection Rules

1. **Require a pull request before merging**
   - ✅ Check "Require a pull request before merging"
   - **Required number of approving reviews:** `2`
   - ✅ Check "Dismiss stale pull request approvals when new commits are pushed"
   - ✅ Check "Require review from Code Owners" (if CODEOWNERS file exists)
   - ✅ Check "Require last push approval" (optional but recommended)

2. **Require status checks to pass before merging**
   - ✅ Check "Require status checks to pass before merging"
   - ✅ Check "Require branches to be up to date before merging"
   - Select the following required status checks:
     - `backend-tests`
     - `frontend-tests`
     - `docker-build`
   - ✅ Check "Require conversation resolution before merging"

3. **Require linear history**
   - ✅ Check "Require linear history" (optional, prevents merge commits)

4. **Require signed commits**
   - ⬜ Optional: "Require signed commits" (recommended for production)

5. **Lock branch**
   - ⬜ Leave unchecked (allows PR merging)

6. **Do not allow bypassing the above settings**
   - ✅ Check "Do not allow bypassing the above settings" (applies to admins too)
   - ✅ Check "Restrict pushes that create matching branches"

7. **Allow force pushes**
   - ❌ Leave unchecked (never allow force pushes to main)

8. **Allow deletions**
   - ❌ Leave unchecked (protect main branch from deletion)

9. **Allow deployment branches to be created**
   - ⬜ Leave unchecked (unless you use GitHub deployments)

10. **Rules applied to everyone including administrators**
    - ✅ Check this box to ensure admins follow the same rules

Click **Create** or **Save changes**

### Step 3: Configure Staging Branch Protection

#### Branch Name Pattern
- Enter `staging` in the "Branch name pattern" field

#### Protection Rules

1. **Require a pull request before merging**
   - ✅ Check "Require a pull request before merging"
   - **Required number of approving reviews:** `1`
   - ✅ Check "Dismiss stale pull request approvals when new commits are pushed"
   - ⬜ "Require review from Code Owners" (optional for staging)

2. **Require status checks to pass before merging**
   - ✅ Check "Require status checks to pass before merging"
   - ✅ Check "Require branches to be up to date before merging"
   - Select the following required status checks:
     - `backend-tests`
     - `frontend-tests`
     - `docker-build`
   - ✅ Check "Require conversation resolution before merging"

3. **Require linear history**
   - ⬜ Optional: Leave unchecked for staging (allows merge commits)

4. **Allow force pushes**
   - ❌ Leave unchecked (never allow force pushes)

5. **Allow deletions**
   - ❌ Leave unchecked (protect staging branch from deletion)

6. **Rules applied to everyone including administrators**
   - ⬜ Leave unchecked (admins can bypass if needed for hotfixes)

Click **Create** or **Save changes**

## Creating the Staging Branch

Before setting up protection rules, ensure the `staging` branch exists:

### Option 1: Using Git (Recommended)

```bash
# Ensure you're on main and up to date
git checkout main
git pull origin main

# Create staging branch from main
git checkout -b staging

# Push staging branch to remote
git push -u origin staging
```

### Option 2: Using GitHub UI

1. Go to your repository on GitHub
2. Click on the branch dropdown (shows current branch, e.g., "main")
3. Type `staging` in the "Find or create a branch" field
4. Click "Create branch: staging from 'main'"

### Option 3: Using Setup Script

Run the provided setup script:

```bash
chmod +x scripts/setup_git_workflow.sh
./scripts/setup_git_workflow.sh
```

## Verification

After setting up branch protection rules, verify they're working:

1. Try to push directly to `main` or `staging`:
   ```bash
   git checkout main
   git commit --allow-empty -m "Test direct push"
   git push origin main
   ```
   This should be **blocked** by GitHub.

2. Create a test PR:
   - Create a feature branch
   - Make a small change
   - Open a PR to `staging`
   - Verify that status checks are required
   - Verify that approval requirements are enforced

## Summary of Protection Rules

### Main Branch
- ✅ Require PR: Yes (2 approvals)
- ✅ Require status checks: Yes (backend-tests, frontend-tests, docker-build)
- ✅ Require up-to-date: Yes
- ✅ Require conversation resolution: Yes
- ✅ Require linear history: Optional
- ✅ Lock branch: No
- ❌ Force pushes: Not allowed
- ❌ Deletions: Not allowed
- ✅ Admin restrictions: Yes

### Staging Branch
- ✅ Require PR: Yes (1 approval)
- ✅ Require status checks: Yes (backend-tests, frontend-tests, docker-build)
- ✅ Require up-to-date: Yes
- ✅ Require conversation resolution: Yes
- ❌ Force pushes: Not allowed
- ❌ Deletions: Not allowed
- ⬜ Admin restrictions: Optional (can allow bypass for emergencies)

## Troubleshooting

### Status Checks Not Showing Up

If status checks don't appear as options:
1. Ensure the CI workflow has run at least once
2. Check that workflow files are in `.github/workflows/`
3. Verify workflow YAML syntax is correct
4. Wait a few minutes after pushing to trigger workflows

### Can't Merge PR Even After Approval

Common causes:
- Status checks haven't completed yet
- Branch is out of date (need to sync with base branch)
- Conversation not resolved (all review comments must be addressed)
- Required status checks haven't passed

### Need to Bypass Rules for Emergency Hotfix

If you're an admin and need to bypass rules:
1. Go to repository Settings → Branches
2. Edit the branch protection rule
3. Temporarily uncheck "Do not allow bypassing" (for main) or allow admin bypass (for staging)
4. Perform your emergency merge
5. **Immediately** re-enable the protection rules

## Additional Resources

- [GitHub Branch Protection Documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [GitHub Status Checks](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/about-status-checks)
- [GitHub CODEOWNERS](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)

