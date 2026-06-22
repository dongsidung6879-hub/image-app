from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from main import app
from database import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
test_engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

Base.metadata.create_all(bind=test_engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch("main.save_image_bytes", new_callable=AsyncMock)
@patch("main.GenerationService.generate_content", new_callable=AsyncMock)
def test_generate_image_success(mock_generate, mock_save):
    mock_generate.return_value = b"fake_bytes"
    mock_save.return_value = "uploads/test.png"

    response = client.post("/generate-image", json={"prompt": "a cute cat", "file_path": ""})
    assert response.status_code == 200
    data = response.json()
    assert data["prompt"] == "a cute cat"
    assert data["file_path"] == "uploads/test.png"
    assert "id" in data
    
def test_get_images():
    response = client.get("/images")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
