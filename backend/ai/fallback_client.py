import os
import logging
import httpx

logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("LLM_API_KEY", "")

def call_openai_api(prompt: str) -> dict:
    """Fallback to OpenAI DALL-E"""
    logger.info(f"Calling Fallback OpenAI API for prompt: {prompt}")
    if not OPENAI_API_KEY:
        raise Exception("OpenAI API Key not configured")
        
    url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "dall-e-3",
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024"
    }
    
    response = httpx.post(url, headers=headers, json=payload, timeout=30.0)
    response.raise_for_status()
    
    return response.json()
