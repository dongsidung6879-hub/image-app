from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ImageRecordBase(BaseModel):
    prompt: str
    file_path: str

class ImageRecordCreate(ImageRecordBase):
    pass

class ImageRecordResponse(ImageRecordBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
