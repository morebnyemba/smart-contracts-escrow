# CI/CD and Auto-merge Workflows

This document describes the Continuous Integration (CI) workflows and the auto-merge feature available for this repository.

## CI Workflows

### Backend CI (`backend-ci.yml`)

The backend CI workflow runs automatically on:
- Push to `main` branch (when backend files change)
- Pull requests that modify backend files

**What it does:**
1. Sets up Python 3.11
2. Caches pip dependencies for faster builds
3. Installs dependencies from `backend/requirements.txt`
4. Lints Python code with flake8 (checks for syntax errors and code quality)
5. Runs Django tests using `python manage.py test`
6. Uploads test artifacts for debugging

**Requirements:**
- Backend code should pass flake8 linting (no syntax errors or undefined names)
- All Django tests must pass

### Frontend CI (`frontend-ci.yml`)

The frontend CI workflow runs automatically on:
- Push to `main` branch (when frontend files change)
- Pull requests that modify frontend files

**What it does:**
1. Sets up Node.js 20
2. Caches npm dependencies for faster builds
3. Installs dependencies with `npm ci` (clean install)
4. Lints code with ESLint
5. Type checks and builds the Next.js application
6. Runs tests (if test script exists)
7. Uploads build artifacts

**Requirements:**
- Frontend code should pass ESLint checks
- TypeScript code should type check successfully
- Next.js application should build without errors

## Auto-merge Workflow

The auto-merge workflow (`automerge-on-label.yml`) provides intelligent, automated PR merging based on configurable criteria.

### How It Works

The workflow automatically evaluates PRs when:
- A label is added or removed
- The PR is synchronized (new commits pushed)
- The PR is opened or marked ready for review

### Merge Criteria

For a PR to be automatically merged, it must meet ALL of the following criteria:

1. ✅ **At least 1 approval** from a reviewer
2. ✅ **No change requests** from any reviewer
3. ✅ **Zero failing check runs** (all CI checks must pass or be neutral)
4. ✅ **Not in draft state**

### What the Workflow Does

1. **Evaluation**: Fetches PR details, reviews, check runs, and changed files
2. **Summary Comment**: Posts a detailed comment with:
   - Current approval count
   - Change request status
   - Failing checks count
   - List of approvers and change requesters
   - Total changed lines and files
   - Status of all check runs
   - Heuristic flags (e.g., large changes, many files)
3. **Decision**:
   - **If criteria pass**: Asserts the `automerge` label and merges the PR using squash merge
   - **If criteria fail**: Creates a review requesting changes with a checklist of what needs to be fixed

### Using Auto-merge

The auto-merge workflow runs automatically on eligible PRs. You don't need to add any labels manually - the workflow will:

1. Evaluate the PR against the merge criteria
2. Post a detailed summary comment
3. If all criteria are met, add the `automerge` label and merge the PR
4. If criteria are not met, post a review requesting changes with specific items to address

### Merge Method

By default, PRs are merged using the **squash** method, which combines all commits into a single commit on the base branch. This can be configured in the workflow file if needed.

### Heuristic Flags

The workflow includes helpful heuristic warnings for:
- **Large changes**: PRs with >1000 lines changed
- **Many files**: PRs modifying >20 files

These are informational and don't block the merge, but serve as reminders to review carefully.

### Permissions

The workflow uses minimal, least-privilege permissions:
- `contents: write` - To merge PRs
- `pull-requests: write` - To create reviews and add labels
- `checks: read` - To read check run status
- `issues: write` - To post comments

### Security

- The workflow only uses the `GITHUB_TOKEN` (no external secrets required)
- Merges are performed via the trusted `peter-evans/merge@v4` action
- All operations are logged for audit purposes

## Dependabot Configuration

Dependabot is configured to automatically create PRs for dependency updates:

- **Frontend (npm)**: Weekly updates on Monday at 09:00
- **Backend (pip)**: Weekly updates on Monday at 09:00

Dependabot PRs are automatically labeled with `dependencies` and either `frontend` or `backend` labels.

## Best Practices

1. **For Contributors**:
   - Ensure CI checks pass before requesting review
   - Address reviewer feedback promptly
   - Keep PRs focused and reasonably sized

2. **For Reviewers**:
   - Review PRs promptly
   - Use "Approve" when satisfied with changes
   - Use "Request Changes" for blocking issues
   - Use "Comment" for non-blocking suggestions

3. **For Maintainers**:
   - Monitor the auto-merge workflow logs
   - Adjust merge criteria in the workflow file if needed
   - Keep CI workflows updated as project structure evolves

## Troubleshooting

**Q: Why wasn't my PR auto-merged even though I got approval?**
A: Check the evaluation summary comment. Common reasons:
- CI checks are still running or have failed
- A reviewer requested changes
- The PR is in draft state

**Q: Can I manually merge a PR?**
A: Yes! The auto-merge workflow is a convenience feature. You can always merge PRs manually through the GitHub UI or CLI.

**Q: How do I disable auto-merge for a specific PR?**
A: The workflow evaluates all PRs automatically, but won't merge unless all criteria are met. If you want to prevent auto-merge, you can convert the PR to draft or ensure at least one reviewer has requested changes.

**Q: CI workflow failed on a step. What should I do?**
A: Check the workflow logs in the "Actions" tab. Common issues:
- Backend: Missing dependencies, test failures, linting errors
- Frontend: ESLint errors, TypeScript errors, build failures

Fix the issues locally, commit, and push. The CI will run again automatically.
