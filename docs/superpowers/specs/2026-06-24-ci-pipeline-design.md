# CI/CD Pipeline Design

## Goal
Establish a fast, reliable, and cost-effective Continuous Integration (CI) pipeline using GitHub Actions to ensure code quality for both the Frontend (React/TypeScript) and Backend (FastAPI/Python) before any code is merged into the `main` branch.

## Architecture

This pipeline follows **Approach A (Paths Filter + Meta-Job)**. It uses a single GitHub Actions workflow (`.github/workflows/ci.yml`) triggered on `push` and `pull_request` to the `main` branch. It utilizes **Paths Filter** to ensure jobs only run when relevant files are modified, keeping execution cost-effective.

### Concurrency
To save GitHub Action minutes, a `concurrency` group will be configured. If a developer pushes multiple commits to the same Pull Request in rapid succession, any previously running jobs for that PR will be automatically cancelled.

### 1. Frontend Job (`frontend-tests`)
- **Environment:** `ubuntu-latest`, Node.js v20.
- **Trigger Condition:** Runs only if files in `frontend/**` or `.github/workflows/**` change.
- **Steps:**
  1. Checkout code.
  2. Setup Node.js v20 with `cache: 'npm'`.
  3. Run `npm ci` inside `frontend/` to strictly install dependencies.
  4. Run `npm run lint` (ESLint).
  5. Run `npm run build` (TypeScript compilation & Vite build).

### 2. Backend Job (`backend-tests`)
- **Environment:** `ubuntu-latest`, Python 3.13.
- **Trigger Condition:** Runs only if files in `backend/**` or `.github/workflows/**` change.
- **Steps:**
  1. Checkout code.
  2. Setup Python 3.13 with `cache: 'pip'`.
  3. Run `pip install -r requirements.txt` inside `backend/`.
  4. Run `pytest`.
  > **Note on PYTHONPATH:** Instead of setting `PYTHONPATH=.` manually in the CI, a `pytest.ini` file will be created in the `backend/` directory with `pythonpath = .` defined. This ensures that test execution logic is consistent and synchronized between local development and the CI environment.

### 3. Meta-Job (`ci-status-check`)
- **Purpose:** Acts as the single Required Status Check for GitHub Branch Protection. This solves the issue where skipped jobs (due to Paths Filter) block PRs from merging.
- **Dependencies:** `needs: [frontend-tests, backend-tests]`
- **Execution:** Runs `if: always()`.
- **Logic:** Evaluates the status of its dependencies. If any needed job fails, it exits with an error. If they pass or are skipped, it exits successfully.

> [!WARNING]
> **Maintenance Note:** When renaming existing jobs or adding new jobs (e.g., `e2e-tests`) to this workflow, you MUST update the `needs: [...]` array in the `ci-status-check` job. If you forget this, the new job will not be evaluated as part of the overall PR status check.

## Secrets & Permissions
Currently, this is a lightweight unit/static-analysis pipeline. However, as the backend uses FastAPI and may connect to real databases or use sensitive keys (like HuggingFace API keys) for integration testing later:
- **GitHub Secrets:** Any sensitive environment variables should be injected via GitHub Repository Secrets (`${{ secrets.HUGGINGFACE_API_KEY }}`) and passed into the backend job via the `env:` block.

## Future Considerations
- Expand to include End-to-End (E2E) testing (e.g., Playwright) as a separate job.
- Integrate test coverage reporting to block PRs if coverage drops below a certain threshold.
