from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ImageRecordCreate(BaseModel):
    prompt: str

class ImageRecordResponse(BaseModel):
    id: int
    prompt: str
    file_path: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
