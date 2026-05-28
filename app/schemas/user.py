import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Min 8 chars")

class UserUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=2)
    password: str | None = Field(None, min_length=8)

class UserResponse(UserBase):
    """Returned to clients — never expose hashed_password."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_active: bool
    created_at: datetime

class UserListResponse(BaseModel):
    total: int
    items: list[UserResponse]

