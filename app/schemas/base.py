from pydantic import BaseModel as PydanticBaseModel
from datetime import datetime

class BaseSchema(PydanticBaseModel):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
