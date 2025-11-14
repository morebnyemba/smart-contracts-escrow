# CI/CD and Auto-merge Workflows

This document describes the Continuous Integration (CI) workflows and the auto-merge feature available for this repository.

## CI Workflows

### Backend CI (`backend-ci.yml`)

The backend CI workflow runs automatically on:
- Push events that modify `backend/**` files
- Pull requests that modify `backend/**` files

**What it does:**
1. Sets up Python 3.11
2. Caches pip dependencies for faster builds (using hash of `backend/requirements.txt`)
3. Installs dependencies from `backend/requirements.txt` (if present)
4. Lints Python code with flake8 (if available)
   - Checks for critical errors (E9, F63, F7, F82)
   - Reports code complexity and style issues
5. Runs tests:
   - First attempts pytest (if available and tests exist)
   - Falls back to Django's `manage.py test` if pytest not available
   - Skips gracefully if no tests found
6. Uploads logs and artifacts for debugging (excludes cache directories)

**Defensive features:**
- Only runs steps when necessary files/directories exist
- Gracefully handles missing dependencies or test files
- Continues workflow even if linting finds issues (for visibility)
- Uses `if: always()` to ensure all steps run even if previous steps fail

### Frontend CI (`frontend-ci.yml`)

The frontend CI workflow runs automatically on:
- Push events that modify `frontend/**` files
- Pull requests that modify `frontend/**` files

**What it does:**
1. Sets up Node.js 18.x
2. Caches npm dependencies for faster builds (using `package-lock.json` hash)
3. Installs dependencies:
   - Uses `npm ci` if `package-lock.json` exists (clean install)
   - Falls back to `npm install` otherwise
4. Lints code with ESLint (if lint script exists in `package.json`)
5. Type checks and builds:
   - Checks for `tsconfig.json` (TypeScript configuration)
   - Attempts `npm run build` first
   - Falls back to `npm run typecheck` if build not available
6. Runs tests (if test script exists, uses `--passWithNoTests` flag)
7. Uploads artifacts (excludes `node_modules` and `.next`)

**Defensive features:**
- Only runs steps when configuration files exist
- Uses `--if-present` flag to gracefully handle missing npm scripts
- Checks for test script existence before running
- Continues workflow even if individual steps fail

## Auto-merge Workflow

The auto-merge workflow (`automerge-on-label.yml`) provides intelligent, automated PR merging based on strict evaluation criteria. **This workflow performs its own review and does not rely on pre-existing labels** - it will assert the `automerge` label only when all criteria are met.

### How It Works

The workflow automatically evaluates PRs when:
- A label is added or removed
- The PR is synchronized (new commits pushed)
- The PR is opened or marked ready for review
- The PR transitions from draft to ready

The workflow will **not** run on draft PRs.

### Merge Criteria

For a PR to be automatically merged, it must meet ALL of the following criteria:

1. ✅ **At least 1 unique approval** from a reviewer (using latest review per user)
2. ✅ **Zero change requests** from any reviewer (using latest review per user)
3. ✅ **Zero failing check runs** (checks must be success, neutral, or skipped)
4. ✅ **Not in draft state**

### What the Workflow Does

The workflow performs a comprehensive evaluation in these steps:

1. **Evaluation** (using `actions/github-script@v7`):
   - Fetches all PR reviews and determines latest review state per user
   - Calculates unique approvals and change requests
   - Fetches all check runs for the PR's head SHA
   - Identifies failing checks (excluding success, neutral, and skipped)
   - Fetches changed files and calculates total changed lines
   - Determines if merge criteria are met

2. **Summary Comment**: Posts a detailed evaluation comment with:
   - Overall criteria status (PASS/FAIL)
   - Approval count and list of approvers
   - Change request count and list of change requesters
   - Failing check count and list of failing checks
   - PR details: changed files count, total changed lines
   - Heuristic flags (large changes, many files)
   - Status of all check runs
   - Clear indication of next steps

3. **Label Assertion**: If all criteria are met, the workflow adds the `automerge` label to the PR

4. **Decision**:
   - **If criteria PASS**: 
     - Posts summary comment showing all criteria met ✅
     - Adds the `automerge` label
     - Merges the PR using squash merge method via `peter-evans/merge@v4`
   - **If criteria FAIL**:
     - Posts summary comment showing which criteria failed ❌
     - Creates a review requesting changes with a checklist of items to address
     - Does NOT add the `automerge` label

### Using Auto-merge

**You don't need to do anything special to use auto-merge!**

The workflow runs automatically on all non-draft PRs. Simply:

1. Open a PR and ensure it's not in draft state
2. Get at least one approval from a reviewer
3. Ensure all CI checks pass
4. Ensure no reviewers have requested changes

The workflow will:
- Automatically evaluate your PR on each event (new commit, label change, etc.)
- Post a summary comment showing the evaluation results
- If all criteria are met, add the `automerge` label and merge the PR
- If criteria are not met, create a review with a checklist of what needs to be addressed

**The workflow evaluates ALL PRs, not just those with a label.** The `automerge` label is added by the workflow itself when it determines the PR is ready to merge.

### Merge Method

PRs are merged using the **squash** method, which combines all commits into a single commit on the base branch.

### Heuristic Flags

The workflow includes helpful heuristic warnings in the summary comment:

- ⚠️ **Large changes**: PRs with >1000 lines changed
- ⚠️ **Many files**: PRs modifying >20 files

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
- All operations are logged in the workflow run for audit purposes
- The workflow performs its own evaluation and doesn't trust pre-existing labels

## Dependabot Configuration

Dependabot is configured in `.github/dependabot.yml` to automatically create PRs for dependency updates:

- **Frontend (npm)**: Weekly updates for dependencies in `/frontend` directory
- **Backend (pip)**: Weekly updates for dependencies in `/backend` directory

The configuration uses:
- `package-ecosystem: 'npm'` for frontend JavaScript/TypeScript dependencies
- `package-ecosystem: 'pip'` for backend Python dependencies
- `schedule: interval: 'weekly'` for regular dependency updates

Dependabot PRs can be evaluated by the auto-merge workflow like any other PR.

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

A: Check the evaluation summary comment posted by the workflow. Common reasons:
- CI checks are still running, pending, or have failed
- A reviewer requested changes (look for change requesters list)
- The PR is in draft state
- No approvals have been recorded (ensure reviewer clicked "Approve")

**Q: Can I manually merge a PR?**

A: Yes! The auto-merge workflow is a convenience feature. You can always merge PRs manually through the GitHub UI or using `gh` CLI.

**Q: How do I disable auto-merge for a specific PR?**

A: The workflow evaluates all PRs automatically, but won't merge unless all criteria are met. To prevent auto-merge:
- Convert the PR to draft, OR
- Request changes as a reviewer, OR
- Ensure at least one CI check fails

The workflow will not add the `automerge` label unless all criteria pass.

**Q: The workflow says I need approvals, but I see approvals on my PR. What's wrong?**

A: The workflow uses the **latest review per user**. If a user approved and then later commented without selecting "Approve" again, their latest review might not be an approval. Ask them to submit an approval review.

**Q: CI workflow failed on a step. What should I do?**

A: Check the workflow logs in the "Actions" tab. Common issues:

**Backend CI:**
- Missing dependencies (check `backend/requirements.txt`)
- Test failures (review pytest/Django test output)
- Linting errors from flake8 (syntax errors, undefined names)

**Frontend CI:**
- ESLint errors (code style/quality issues)
- TypeScript errors (type checking failures)
- Build failures (Next.js build issues)
- Missing or outdated dependencies

Fix the issues locally, commit, and push. The CI will run again automatically.

**Q: The auto-merge workflow keeps posting evaluation comments. Can I disable this?**

A: The workflow posts a comment each time it evaluates the PR (on each trigger event). This is by design to provide visibility into the merge status. If you find this too noisy, you can modify the workflow file to comment less frequently or only when the status changes.

**Q: What if I want to change the merge criteria?**

A: The merge criteria are defined in the `automerge-on-label.yml` workflow file. You can modify the evaluation logic in the first step to adjust:
- Required approval count (default: ≥1)
- How change requests are handled
- Which check run conclusions are considered failures
- Additional criteria like required reviewers, PR size limits, etc.

After modifying the workflow, test it on a test PR to ensure it works as expected.
