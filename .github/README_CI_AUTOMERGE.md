# CI/CD and Auto-merge Documentation

This document describes the GitHub Actions workflows and Dependabot configuration for the smart-contracts-escrow repository.

## 📋 Table of Contents

- [Workflows Overview](#workflows-overview)
- [Backend CI](#backend-ci)
- [Frontend CI](#frontend-ci)
- [Auto-merge Workflow](#auto-merge-workflow)
- [Dependabot Configuration](#dependabot-configuration)
- [Usage Guide](#usage-guide)

## Workflows Overview

This repository includes three main workflows:

1. **Backend CI** (`.github/workflows/backend-ci.yml`) - Automated testing and linting for Python/Django backend
2. **Frontend CI** (`.github/workflows/frontend-ci.yml`) - Automated testing, linting, and building for Next.js frontend
3. **Auto-merge on Label** (`.github/workflows/automerge-on-label.yml`) - Intelligent auto-merge based on PR evaluation

## Backend CI

### Triggers
- Push events affecting `backend/**` files
- Pull request events affecting `backend/**` files

### Steps
1. **Checkout** - Retrieves the repository code
2. **Setup Python 3.11** - Configures Python environment
3. **Cache pip packages** - Speeds up dependency installation
4. **Install dependencies** - Installs packages from `backend/requirements.txt`
5. **Lint with flake8** - Checks code quality and style
   - Strict checks for syntax errors and undefined names
   - Warning checks for complexity and line length
6. **Run tests with pytest** - Executes Django tests
   - Supports both pytest and Django's built-in test runner
7. **Upload test logs** - Preserves test artifacts for debugging

### Permissions
- `contents: read` - Read repository contents
- `pull-requests: write` - Comment on pull requests
- `checks: read` - Read check run status

## Frontend CI

### Triggers
- Push events affecting `frontend/**` files
- Pull request events affecting `frontend/**` files

### Steps
1. **Checkout** - Retrieves the repository code
2. **Setup Node.js 18.x** - Configures Node.js environment
3. **Cache npm packages** - Speeds up dependency installation
4. **Install dependencies** - Runs `npm ci` or `npm install`
5. **Lint code** - Executes linting if script is present
6. **Type check** - Runs TypeScript type checking
7. **Build application** - Builds the Next.js application
8. **Run tests** - Executes test suite if present
9. **Upload test logs** - Preserves test artifacts and coverage reports

### Permissions
- `contents: read` - Read repository contents
- `pull-requests: write` - Comment on pull requests
- `checks: read` - Read check run status

## Auto-merge Workflow

### Overview
This workflow evaluates pull requests and automatically merges them when they meet specific criteria. It operates on an **opt-in** basis by asserting the `automerge` label only after its evaluation passes.

### Triggers
- `labeled` - When a label is added
- `unlabeled` - When a label is removed
- `synchronize` - When new commits are pushed
- `opened` - When a PR is opened
- `ready_for_review` - When a draft PR is marked as ready

### Evaluation Criteria

The workflow evaluates PRs based on:

1. **Approvals**: At least 1 unique approval required
2. **Change Requests**: No active change requests
3. **Failing Checks**: Zero failing or cancelled check runs
4. **Changed Lines**: Tracked for information purposes

### Workflow Behavior

#### ✅ When Criteria Pass:
1. Posts an evaluation comment showing the status
2. **Adds the `automerge` label** to the PR
3. Enables auto-merge with squash method
4. PR merges automatically

#### ❌ When Criteria Fail:
1. Posts an evaluation comment showing the status
2. Creates a review with `REQUEST_CHANGES` status
3. Provides a checklist of items to address
4. Re-evaluates automatically when changes are made

### Merge Method
- **Squash merge** - All commits are squashed into a single commit on the base branch

### Permissions
- `contents: write` - Required for merging
- `pull-requests: write` - Required for adding labels and comments
- `checks: read` - Required for reading check status

## Dependabot Configuration

Dependabot is configured to automatically check for dependency updates weekly.

### Frontend (npm)
- **Directory**: `/frontend`
- **Schedule**: Weekly on Mondays at 09:00
- **Open PR limit**: 5
- **Labels**: `dependencies`, `javascript`
- **Commit prefix**: `chore`

### Backend (pip)
- **Directory**: `/backend`
- **Schedule**: Weekly on Mondays at 09:00
- **Open PR limit**: 5
- **Labels**: `dependencies`, `python`
- **Commit prefix**: `chore`

### Reviewers
All Dependabot PRs are automatically assigned to `@morebnyemba` for review.

## Usage Guide

### For Contributors

#### Regular PRs
1. Create your feature branch and make changes
2. Push your changes and open a pull request
3. Backend CI and/or Frontend CI will run automatically
4. Address any linting or test failures
5. Request reviews from maintainers

#### Using Auto-merge
1. Open a pull request (ensure it's not a draft)
2. The auto-merge workflow will evaluate your PR automatically
3. Check the evaluation comment to see current status
4. Obtain at least 1 approval from reviewers
5. Ensure all checks pass
6. The workflow will automatically add the `automerge` label and merge your PR

**Note**: You don't need to manually add the `automerge` label - the workflow adds it automatically when criteria are met.

### For Maintainers

#### Reviewing PRs
- Review code changes as usual
- Approve or request changes
- The auto-merge workflow handles merging automatically for approved PRs

#### Adjusting Auto-merge Criteria
If you need to change the auto-merge criteria:
1. Edit `.github/workflows/automerge-on-label.yml`
2. Modify the `criteriaPass` logic in the evaluation step
3. Common adjustments:
   - Change minimum approvals: `approvals >= 2`
   - Change merge method: `merge-method: merge` or `merge-method: rebase`
   - Add additional checks based on changed files or other criteria

#### Disabling Auto-merge for Specific PRs
- Remove the `automerge` label if accidentally added
- The workflow will re-evaluate and not merge if criteria aren't met
- You can also mark PRs as draft to prevent auto-merge

### Troubleshooting

#### Backend CI Fails
- Check that `backend/requirements.txt` is up to date
- Ensure all tests pass locally: `cd backend && pytest`
- Review flake8 errors and fix code style issues

#### Frontend CI Fails
- Check that `frontend/package.json` dependencies are correct
- Ensure the build succeeds locally: `cd frontend && npm run build`
- Review linting errors: `cd frontend && npm run lint`

#### Auto-merge Not Working
- Verify the PR has at least 1 approval
- Check that no reviewers have requested changes
- Ensure all CI checks are passing (green)
- Confirm the PR is not marked as draft

### Security Considerations

All workflows use least-privilege permissions:
- Read access to repository contents
- Write access only where needed (auto-merge for merging, PR comments)
- Tokens are scoped appropriately using `GITHUB_TOKEN`

## Contributing

To improve these workflows:
1. Test changes in a fork or feature branch
2. Open a PR with your improvements
3. Document any new features or changes
4. Ensure backward compatibility where possible

## Support

For questions or issues with CI/CD:
- Open an issue in the repository
- Tag `@morebnyemba` for workflow-specific questions
- Check GitHub Actions logs for detailed error messages
