# CI/CD Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish a fast, reliable, and cost-effective Continuous Integration (CI) pipeline using GitHub Actions to ensure code quality for both the Frontend and Backend.

**Architecture:** Approach A (Paths Filter + Meta-Job) with a single GitHub Actions workflow (`.github/workflows/ci.yml`) and `dorny/paths-filter`. A `pytest.ini` will be added to synchronize Python path locally and in CI.

**Tech Stack:** GitHub Actions, pytest, npm, Python.

## Global Constraints
- `npm ci` must be used.
- Paths Filter must handle frontend and backend independently.
- `ci-status-check` must act as the sole required check for branch protection.

---

### Task 1: Create `pytest.ini`

**Files:**
- Create: `backend/pytest.ini`

**Interfaces:**
- Consumes: N/A
- Produces: `pytest` will automatically use `.` as the pythonpath.

- [ ] **Step 1: Write the implementation**

```ini
[pytest]
pythonpath = .
```

- [ ] **Step 2: Run test to verify it passes**

Run: `pytest` in `backend` directory
Expected: PASS (9 passed)

- [ ] **Step 3: Commit**

```bash
git add backend/pytest.ini
git commit -m "chore: add pytest.ini for consistent pythonpath"
```

### Task 2: Create GitHub Actions Workflow

**Files:**
- Create: `.github/workflows/ci.yml`

**Interfaces:**
- Consumes: `frontend/package-lock.json`, `backend/requirements.txt`
- Produces: A fully functional CI pipeline.

- [ ] **Step 1: Write the implementation**

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

concurrency:
  group: ci-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  changes:
    name: Detect Changed Paths
    runs-on: ubuntu-latest
    outputs:
      frontend: ${{ steps.filter.outputs.frontend }}
      backend: ${{ steps.filter.outputs.backend }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            frontend:
              - 'frontend/**'
              - '.github/workflows/ci.yml'
            backend:
              - 'backend/**'
              - '.github/workflows/ci.yml'

  frontend-tests:
    name: Frontend Checks
    needs: changes
    if: needs.changes.outputs.frontend == 'true'
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        working-directory: frontend
        run: npm ci

      - name: Run lint
        working-directory: frontend
        run: npm run lint

      - name: Run build
        working-directory: frontend
        run: npm run build

  backend-tests:
    name: Backend Checks
    needs: changes
    if: needs.changes.outputs.backend == 'true'
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'
          cache: 'pip'
          cache-dependency-path: backend/requirements.txt

      - name: Install dependencies
        working-directory: backend
        run: pip install -r requirements.txt

      - name: Run tests
        working-directory: backend
        run: pytest

  ci-status-check:
    name: CI Status Check
    runs-on: ubuntu-latest
    needs: [changes, frontend-tests, backend-tests]
    if: always()
    steps:
      - name: Check overall status
        run: |
          if [[ "${{ contains(needs.*.result, 'failure') }}" == "true" || "${{ contains(needs.*.result, 'cancelled') }}" == "true" ]]; then
            echo "❌ Một hoặc nhiều job đã fail hoặc bị hủy."
            exit 1
          fi
          echo "✅ Tất cả các job liên quan đã pass (hoặc bị skip hợp lệ)."
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: add GitHub Actions workflow"
```
