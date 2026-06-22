### Task 1: Khởi tạo Backend FastAPI & Setup Môi trường

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/main.py`
- Create: `backend/.env.example`
- Create: `backend/tests/test_main.py`

**Interfaces:**
- Consumes: Môi trường biến `.env`
- Produces: API Server chạy tại `http://localhost:8000/health`.

- [ ] **Step 1: Khởi tạo file cấu hình và biến môi trường**

```txt
# backend/requirements.txt
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.2
python-dotenv==1.0.0
httpx==0.25.2
pytest==7.4.3
pytest-asyncio==0.23.2
tenacity==8.2.3
```

```env
# backend/.env.example
FAL_KEY=your_fal_api_key_here
LLM_API_KEY=your_llm_api_key_here
```

- [ ] **Step 2: Viết test cho endpoint `/health` (Failing test)**

```python
# backend/tests/test_main.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

- [ ] **Step 3: Viết code implementation cho `main.py`**

```python
# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI Architecture API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}
```

- [x] **Step 4: Chạy test kiểm tra**

Run: `cd backend && python -m pytest tests/test_main.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/
git commit -m "feat(backend): init FastAPI and health check"
```
