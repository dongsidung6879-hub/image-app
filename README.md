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
