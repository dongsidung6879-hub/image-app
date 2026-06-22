from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
from dotenv import load_dotenv
import os

from database import engine, Base, get_db
import models
import schemas
from services.generation_service import GenerationService
from services.storage_service import save_image_bytes

load_dotenv()

# Tạo bảng Database
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Architecture API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/generate-image", response_model=schemas.ImageRecordResponse)
async def generate_image_endpoint(request: schemas.ImageRecordCreate, db: Session = Depends(get_db)):
    service = GenerationService()
    
    try:
        image_bytes = await service.generate_content(request.prompt)
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
        
    try:
        local_path = await save_image_bytes(image_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save image: {e}")
        
    db_image = models.ImageRecord(prompt=request.prompt, file_path=local_path)
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    
    return db_image

@app.get("/images", response_model=List[schemas.ImageRecordResponse])
def get_images(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    images = db.query(models.ImageRecord).order_by(models.ImageRecord.created_at.desc()).offset(skip).limit(limit).all()
    return images
