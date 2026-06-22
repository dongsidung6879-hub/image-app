from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel
from services.generation_service import GenerationService

load_dotenv()

app = FastAPI(title="AI Architecture API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerateImageRequest(BaseModel):
    prompt: str

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/generate-image")
def generate_image(request: GenerateImageRequest):
    service = GenerationService()
    result = service.generate_content(request.prompt)
    return result
