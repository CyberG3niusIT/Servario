import uuid
from app.models.user import UserRole
from pydantic import BaseModel, EmailStr


class UserRead(BaseModel):
    id: uuid.UUID
    email: str
    display_name: str | None
    role: UserRole
    is_active: bool

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    display_name: str | None = None
    role: UserRole = UserRole.STAFF


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
