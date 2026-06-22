import os
import httpx
import uuid
import aiofiles
from pathlib import Path

UPLOAD_DIR = Path("uploads")
# Create directory synchronously on import
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

async def download_and_save_image(url: str) -> str:
    """Download image from URL and save it to the local uploads directory.
    Returns the relative file path for the API."""
    filename = f"{uuid.uuid4()}.png"
    file_path = UPLOAD_DIR / filename
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=30.0)
        response.raise_for_status()
        
        async with aiofiles.open(file_path, 'wb') as out_file:
            await out_file.write(response.content)
            
    return f"uploads/{filename}"

async def save_image_bytes(data: bytes) -> str:
    """Save raw image bytes to the local uploads directory.
    Returns the relative file path for the API."""
    filename = f"{uuid.uuid4()}.png"
    file_path = UPLOAD_DIR / filename
    
    async with aiofiles.open(file_path, 'wb') as out_file:
        await out_file.write(data)
        
    return f"uploads/{filename}"
