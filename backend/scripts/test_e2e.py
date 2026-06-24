import sys
import os

# Đảm bảo import được module từ thư mục backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

sys.stdout.reconfigure(encoding='utf-8')

def test_generation():
    print("Starting E2E test with Hugging Face API...")
    try:
        # Giả lập 1 request từ Frontend tới FastAPI
        payload = {"prompt": "A futuristic cyberpunk city at night, neon lights, 4k resolution, high detail"}
        response = client.post("/generate-image", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ THÀNH CÔNG! Đã tạo và lưu ảnh.")
            print(f"   ID trong CSDL: {data['id']}")
            print(f"   Prompt: {data['prompt']}")
            print(f"   Đường dẫn file lưu tại local: {data['file_path']}")
            
            # Kiểm tra xem file có thực sự tồn tại trên ổ cứng không
            backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            file_abs_path = os.path.join(backend_dir, data['file_path'])
            if os.path.exists(file_abs_path):
                print(f"   🎉 Đã xác minh file tồn tại: {file_abs_path}")
            else:
                print(f"   ❌ LỖI: API báo thành công nhưng không tìm thấy file tại {file_abs_path}")
        else:
            print(f"❌ THẤT BẠI. HTTP Status Code: {response.status_code}")
            print(f"   Chi tiết lỗi: {response.text}")
    except Exception as e:
        print(f"❌ Lỗi hệ thống khi chạy test: {e}")

if __name__ == "__main__":
    test_generation()
