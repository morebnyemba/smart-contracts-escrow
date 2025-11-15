# Smart Contracts Escrow Platform

This is a monorepo for a button-driven escrow platform, featuring a Django backend and a Next.js frontend.

## Project Context

The platform combines a simple, 8-step user flow with the ability to manage complex, milestone-based payments. It includes distinct portals for Buyers and Sellers, a seller onboarding/verification process, and seller discovery features.

## Repository Structure

- **backend**: Django project for the API, user management, transactions, and wallets.
- **frontend**: Next.js project for the user interface, including buyer/seller portals, onboarding, and transaction views.

## Getting Started

Further instructions will be added here for setting up the development environment, running the applications, and deploying.

## CI/CD and Automation

This repository includes GitHub Actions workflows to help maintain code quality and automate routine tasks:

### Continuous Integration Workflows

- **Backend CI** (`.github/workflows/backend-ci.yml`): Automatically runs on changes to the `backend/` directory
  - Sets up Python 3.11 environment
  - Caches pip dependencies for faster builds
  - Installs backend dependencies
  - Runs linting with flake8 (if configured)
  - Executes tests with pytest (if tests exist)

- **Frontend CI** (`.github/workflows/frontend-ci.yml`): Automatically runs on changes to the `frontend/` directory
  - Sets up Node.js 18.x environment
  - Caches npm dependencies for faster builds
  - Installs frontend dependencies
  - Runs linting
  - Performs type checking
  - Executes tests

### Auto-merge Workflow

The **Auto-merge** workflow (`.github/workflows/automerge-on-label.yml`) provides an automated way to merge PRs when they meet quality criteria:

**How it works:**
1. The workflow automatically evaluates all non-draft PRs
2. Checks that the PR meets criteria:
   - At least 1 approval from a reviewer
   - All required checks are passing (no failing status checks)
   - No change requests from reviewers
3. If criteria are met, adds the `automerge` label and merges using the squash method
4. If criteria are not met, posts a review with a checklist of items to address

**When to use:**
- For routine dependency updates from Dependabot
- For small, well-tested changes that have been reviewed
- When you want to ensure a PR merges as soon as all checks pass

### PR Iterator Workflow

The **PR Iterator** workflow (`.github/workflows/pr-iterator.yml`) automatically monitors all open PRs:

**Features:**
- Runs every 15 minutes to check all open PRs (providing faster feedback)
- Identifies stale PRs (>14 days inactive) or PRs waiting for review (>7 days)
- Automatically adds/removes labels: `stale`, `needs-review`, `changes-requested`
- Posts status comments with actionable checklists
- Helps ensure no PR is forgotten or left in limbo

### Auto-approve Workflow

The **Auto-approve Workflow** (`.github/workflows/auto-approve-workflows.yml`) automatically approves workflow runs from forks and first-time contributors, ensuring CI runs immediately without manual intervention.

### Gemini PR Review

The **Gemini PR Review** workflow (`.github/workflows/gemini-pr-review.yml`) provides AI-powered code review using Google's Gemini model. Configure `GEMINI_API_KEY` in repository secrets to enable automatic code reviews on all PRs.

### Dependabot Configuration

Dependabot (`.github/dependabot.yml`) is configured to automatically check for dependency updates weekly:
- **npm packages** in the `frontend/` directory
- **pip packages** in the `backend/` directory

Dependabot will create PRs for dependency updates, which can be reviewed and merged (optionally using the auto-merge label for trusted updates).

*This is a test commit to enable pull request creation.*
