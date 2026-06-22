from ai.client import generate_image

class GenerationService:
    async def generate_content(self, prompt: str) -> bytes:
        return await generate_image(prompt)
