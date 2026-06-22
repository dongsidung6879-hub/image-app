import os
import logging
import httpx

logger = logging.getLogger(__name__)

async def generate_image(prompt: str) -> bytes:
    hf_api_key = os.getenv("HF_API_KEY", "")
    if not hf_api_key:
        raise ValueError("HF_API_KEY is not set")
        
    url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {hf_api_key}"}
    payload = {"inputs": prompt}
    
    response = httpx.post(url, headers=headers, json=payload, timeout=60.0)
    
    if response.status_code == 503:
        raise RuntimeError("Model is currently loading. Please wait a few seconds.")
        
    response.raise_for_status()
    return response.content
