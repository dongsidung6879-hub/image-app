# Image App — Production Roadmap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Take the Image App from a working local prototype to a publicly accessible, production-deployed web application.

**Architecture:**
- **Phase A:** Fix hardcoded frontend config, verify E2E locally, write developer README.
- **Phase B:** Deploy FastAPI backend to Render.com, deploy React/Vite frontend to Vercel, wire them with environment variables.
- **Deployment:** Backend → Render.com (Python free tier). Frontend → Vercel (Vite free tier).

**Tech Stack:** FastAPI, React/Vite, SQLite, Hugging Face Inference API, GitHub Actions, Render.com, Vercel.

## Global Constraints
- Never hardcode URLs — all backend URLs must come from environment variables.
- Frontend env var prefix must be `VITE_` (Vite requirement).
- `frontend/.env` and `backend/.env` must remain in `.gitignore`.
- `frontend/.env.example` and `backend/.env.example` must be kept up to date.
- CORS on backend must explicitly list production frontend URL in production.
- All backend changes must pass `pytest` (9 tests) before committing.

---

## Phase A: Production-Ready Local App

---

### Task 1: Fix Hardcoded Backend URL in Frontend

**Files:**
- Create: `frontend/.env`
- Create: `frontend/.env.example`
- Modify: `frontend/src/components/ImageCard.tsx` (line 10)
- Modify: `frontend/src/services/api.ts` (line 3)

**Interfaces:**
- Consumes: N/A
- Produces: `VITE_API_URL` env var consumed by `api.ts` and `ImageCard.tsx`. Local value: `http://127.0.0.1:8000`.

- [ ] **Step 1: Create `frontend/.env`**

```env
VITE_API_URL=http://127.0.0.1:8000
```

- [ ] **Step 2: Create `frontend/.env.example`**

```env
# URL of the Backend API server
# Local development: http://127.0.0.1:8000
# Production (Render): https://your-app-name.onrender.com
VITE_API_URL=http://127.0.0.1:8000
```

- [ ] **Step 3: Update `frontend/src/services/api.ts`**

Full file after change:
```typescript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
});

export interface ImageRecord {
  id: number;
  prompt: string;
  file_path: string;
  created_at: string;
}

export const generateImage = async (prompt: string): Promise<ImageRecord> => {
  const response = await api.post('/generate-image', { prompt });
  return response.data;
};

export const getImages = async (skip = 0, limit = 50): Promise<ImageRecord[]> => {
  const response = await api.get(`/images?skip=${skip}&limit=${limit}`);
  return response.data;
};
```

- [ ] **Step 4: Update `frontend/src/components/ImageCard.tsx`**

Full file after change:
```tsx
import { Download } from 'lucide-react';
import './ImageCard.css';

interface ImageCardProps {
  imageUrl: string;
  prompt: string;
}

export default function ImageCard({ imageUrl, prompt }: ImageCardProps) {
  const backendUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
  const fullUrl = imageUrl.startsWith('http') ? imageUrl : `${backendUrl}/${imageUrl}`;

  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = fullUrl;
    link.download = `AI_Canvas_${Date.now()}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="image-card animate-fade-in">
      <div className="image-wrapper">
        <img src={fullUrl} alt={prompt} loading="lazy" />
        <div className="image-overlay">
          <button className="download-btn" onClick={handleDownload} title="Download">
            <Download size={20} />
          </button>
        </div>
      </div>
      <div className="image-info">
        <p className="image-prompt" title={prompt}>{prompt}</p>
      </div>
    </div>
  );
}
```

- [ ] **Step 5: Verify frontend lint & build pass**

```bash
# Run from: e:\DU AN AI\IMAGE APP\frontend
npm run lint
npm run build
```
Expected: No errors, `dist/` folder created.

- [ ] **Step 6: Commit**

```bash
git add frontend/.env.example frontend/src/services/api.ts frontend/src/components/ImageCard.tsx
git commit -m "fix(frontend): replace hardcoded backend URL with VITE_API_URL env var"
```

---

### Task 2: Fix Local DNS and Verify Full E2E

**Context:** The E2E test failed with `getaddrinfo failed` — Python DNS cannot reach `api-inference.huggingface.co`. Fix: set system DNS to `8.8.8.8`.

**Files:** No code changes — environment setup + manual browser verification.

**Interfaces:**
- Consumes: `backend/.env` with valid `HF_API_KEY`
- Produces: Confirmed working end-to-end flow (browser → frontend → backend → HF → saved PNG)

- [ ] **Step 1: Fix system DNS on Windows**

1. Start Menu → search "Network connections" → "View network connections".
2. Right-click active adapter → Properties.
3. Select "Internet Protocol Version 4 (TCP/IPv4)" → Properties.
4. Set Preferred DNS: `8.8.8.8`, Alternate: `8.8.4.4`. Click OK.

- [ ] **Step 2: Verify DNS**

```bash
ping api-inference.huggingface.co
```
Expected: Replies with IP address (not "could not find host").

- [ ] **Step 3: Start backend (Terminal 1)**

```bash
# From: e:\DU AN AI\IMAGE APP\backend
..\.venv\Scripts\uvicorn main:app --reload --port 8000
```

- [ ] **Step 4: Start frontend (Terminal 2)**

```bash
# From: e:\DU AN AI\IMAGE APP\frontend
npm run dev
```

- [ ] **Step 5: Test full flow in browser**

1. Open `http://localhost:5173`.
2. Enter: `A futuristic cyberpunk city at night, neon lights, 4k resolution`.
3. Click Generate. Wait up to 90 seconds (HF cold start normal).
4. Expected: Image appears. Navigate to `/gallery` — image in grid. Check `backend/uploads/` for `.png` file.

---

### Task 3: Write Developer README

**Files:**
- Create: `README.md` (at project root `e:\DU AN AI\IMAGE APP\`)

**Interfaces:**
- Consumes: N/A
- Produces: Setup guide for any developer cloning this repo.

- [ ] **Step 1: Create `README.md`**

```markdown
# AI.Canvas — AI Image Generation App

A full-stack web application for generating images from text prompts using the Hugging Face Inference API.

## Tech Stack

- **Frontend:** React + TypeScript + Vite
- **Backend:** FastAPI (Python) + SQLite
- **AI Model:** `stabilityai/stable-diffusion-xl-base-1.0` via Hugging Face Inference API
- **CI/CD:** GitHub Actions (lint + build + pytest on every push/PR)

## Prerequisites

- Python 3.13+
- Node.js 20+
- Free [Hugging Face](https://huggingface.co) account → Settings → Access Tokens → New token (Read permission)

## Local Setup

### 1. Clone

```bash
git clone https://github.com/dongsidung6879-hub/image-app.git
cd image-app
```

### 2. Backend

```bash
cd backend
python -m venv ../.venv
..\.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env: set HF_API_KEY=hf_your_token_here
```

### 3. Frontend

```bash
cd frontend
cp .env.example .env
npm install
```

### 4. Run

**Terminal 1 — Backend:**
```bash
cd backend
..\.venv\Scripts\uvicorn main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

Open `http://localhost:5173`.

> **Network note (Vietnamese ISPs):** If generation fails with a network error, set system DNS to `8.8.8.8`. Some ISPs block Hugging Face at DNS level while browsers bypass via DoH.

## Tests

```bash
cd backend
..\.venv\Scripts\pytest
# Expected: 9 passed
```

## Project Structure

```
image-app/
├── backend/
│   ├── ai/client.py              # HF API client (async + Tenacity retry)
│   ├── utils/circuit_breaker.py  # In-memory circuit breaker
│   ├── services/
│   │   ├── generation_service.py
│   │   └── storage_service.py
│   ├── main.py                   # FastAPI app
│   └── tests/                    # 9 pytest tests
├── frontend/
│   └── src/
│       ├── pages/                # GeneratorPage, GalleryPage
│       ├── components/           # Button, Input, ImageCard
│       └── services/api.ts       # Axios client
└── .github/workflows/ci.yml      # GitHub Actions CI
```
```

- [ ] **Step 2: Commit and push**

```bash
git add README.md frontend/.env.example
git commit -m "docs: add README with local setup guide and project structure"
git push origin master
```

---

## Phase B: Cloud Deployment

---

### Task 4: Prepare Backend for Render Deployment

**Files:**
- Modify: `backend/requirements.txt` — add `gunicorn`
- Create: `backend/render.yaml`
- Modify: `backend/main.py` — dynamic CORS from `FRONTEND_URL` env var

**Interfaces:**
- Consumes: N/A
- Produces: Backend deployable to Render. Reads `FRONTEND_URL` env var for CORS.

- [ ] **Step 1: Add `gunicorn` to `backend/requirements.txt`**

Full file after change:
```
fastapi
uvicorn[standard]
gunicorn
pydantic
python-dotenv
httpx
pytest
pytest-asyncio
tenacity
sqlalchemy
aiofiles
```

- [ ] **Step 2: Create `backend/render.yaml`**

```yaml
services:
  - type: web
    name: image-app-backend
    runtime: python
    rootDir: backend
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn main:app -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
    envVars:
      - key: HF_API_KEY
        sync: false
      - key: DATABASE_URL
        value: sqlite:///./image_app.db
      - key: FRONTEND_URL
        sync: false
```

- [ ] **Step 3: Update CORS in `backend/main.py`**

Replace the `allow_origins=["*"]` block (around line 22) with:
```python
# Dynamic CORS — supports comma-separated origins
_raw_origins = os.getenv("FRONTEND_URL", "http://localhost:5173")
allowed_origins = [o.strip() for o in _raw_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

- [ ] **Step 4: Run tests**

```bash
..\.venv\Scripts\pytest
```
Expected: 9 passed.

- [ ] **Step 5: Commit and push**

```bash
git add backend/requirements.txt backend/render.yaml backend/main.py
git commit -m "feat(backend): add Render deploy config and dynamic CORS via FRONTEND_URL"
git push origin master
```

---

### Task 5: Deploy Backend to Render

**Files:** No code changes.

**Interfaces:**
- Produces: `RENDER_BACKEND_URL` (e.g., `https://image-app-backend-xxxx.onrender.com`) — required by Task 6.

- [ ] **Step 1:** Create account at [render.com](https://render.com) → Sign up with GitHub.

- [ ] **Step 2:** Dashboard → **New** → **Web Service** → Connect `dongsidung6879-hub/image-app`.

Settings:
- Name: `image-app-backend`
- Root Directory: `backend`
- Runtime: Python 3
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn main:app -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`
- Instance Type: Free

- [ ] **Step 3:** Under Environment tab, add:
- `HF_API_KEY` = `hf_your_token_here`
- `DATABASE_URL` = `sqlite:///./image_app.db`
- `FRONTEND_URL` = *(leave blank — set after Vercel deploy)*

- [ ] **Step 4:** Click **Create Web Service**. Wait 3–5 minutes.

- [ ] **Step 5:** Verify: Open `https://image-app-backend-xxxx.onrender.com/health`
Expected: `{"status": "ok"}`

---

### Task 6: Deploy Frontend to Vercel

**Files:** No code changes.

**Interfaces:**
- Consumes: `RENDER_BACKEND_URL` from Task 5.
- Produces: `VERCEL_FRONTEND_URL` — needed to update `FRONTEND_URL` on Render.

- [ ] **Step 1:** Create account at [vercel.com](https://vercel.com) → Sign up with GitHub.

- [ ] **Step 2:** Dashboard → **Add New Project** → Import `dongsidung6879-hub/image-app`.

Settings:
- Framework Preset: Vite
- Root Directory: `frontend`
- Build Command: `npm run build`
- Output Directory: `dist`

- [ ] **Step 3:** Environment Variables:
- `VITE_API_URL` = your Render URL (e.g., `https://image-app-backend-xxxx.onrender.com`)

- [ ] **Step 4:** Click **Deploy**. Note the Vercel URL (e.g., `https://image-app-xxxx.vercel.app`).

- [ ] **Step 5:** Go back to Render → your backend → Environment tab. Set:
- `FRONTEND_URL` = your Vercel URL. Save → auto-redeploy.

---

### Task 7: Verify Full E2E on Production

**Files:** No code changes.

- [ ] **Step 1:** `https://image-app-backend-xxxx.onrender.com/health` → `{"status":"ok"}`

- [ ] **Step 2:** Open Vercel URL → generate image with prompt `A serene Japanese garden, watercolor style` → wait up to 90s → image appears.

- [ ] **Step 3:** Navigate to `/gallery` → image appears in grid.

- [ ] **Step 4:** Click download button → PNG downloads.

- [ ] **Step 5:** If any fixes needed, commit and push:
```bash
git add -A
git commit -m "fix(production): post-deployment adjustments"
git push origin master
```

---

## Verification Summary

| Phase | Check | Expected |
|-------|-------|----------|
| A | `npm run lint && npm run build` | 0 errors |
| A | `pytest` | 9 passed |
| A | Browser E2E local | Image generated → gallery → download |
| B | `/health` on Render | `{"status":"ok"}` |
| B | Browser E2E on Vercel | Full flow on production |
| B | GitHub Actions CI | All checks green |
