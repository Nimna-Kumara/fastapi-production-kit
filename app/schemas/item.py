import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ItemsBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=255)

class ItemCrete(ItemsBase):
    pass

class ItemUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None

class ItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime

class ItemlistResponse(BaseModel):
    total: int
    items: list[ItemResponse] 