import uuid
from decimal import Decimal
from pydantic import BaseModel, Field


class ServiceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    duration_minutes: int = Field(..., gt=0)
    price: Decimal | None = None
    currency: str | None = Field(None, max_length=3)
    is_active: bool = True


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    duration_minutes: int | None = Field(None, gt=0)
    price: Decimal | None = None
    currency: str | None = None
    is_active: bool | None = None


class ServiceRead(ServiceBase):
    id: uuid.UUID

    model_config = {"from_attributes": True}
