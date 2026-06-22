from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch("main.GenerationService.generate_content")
def test_generate_image_success(mock_generate):
    mock_generate.return_value = {"status": "success", "data": {"images": [{"url": "http://img.png"}]}}
    response = client.post("/generate-image", json={"prompt": "a cute cat"})
    assert response.status_code == 200
    assert response.json() == {"status": "success", "data": {"images": [{"url": "http://img.png"}]}}
    mock_generate.assert_called_once_with("a cute cat")
