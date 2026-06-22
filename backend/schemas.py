from pydantic import BaseModel
from datetime import datetime

class ImageRecordBase(BaseModel):
    prompt: str
    file_path: str

class ImageRecordCreate(ImageRecordBase):
    pass

class ImageRecordResponse(ImageRecordBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
