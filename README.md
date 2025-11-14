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

**How to use:**
1. Add the `automerge` or `auto-merge` label to a pull request
2. The workflow will automatically check:
   - At least 1 approval from a reviewer
   - All required checks are passing (no failing status checks)
3. If criteria are met, the PR will be automatically merged using the squash method
4. If criteria are not met, the workflow waits for the next update or label change

**When to use auto-merge:**
- For routine dependency updates from Dependabot
- For small, well-tested changes that have been reviewed
- When you want to ensure a PR merges as soon as all checks pass

### Dependabot Configuration

Dependabot (`.github/dependabot.yml`) is configured to automatically check for dependency updates weekly:
- **npm packages** in the `frontend/` directory
- **pip packages** in the `backend/` directory

Dependabot will create PRs for dependency updates, which can be reviewed and merged (optionally using the auto-merge label for trusted updates).

*This is a test commit to enable pull request creation.*
