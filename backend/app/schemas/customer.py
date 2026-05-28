import uuid
from datetime import datetime
from pydantic import BaseModel


class CustomerCreate(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None
    notes: str | None = None


class CustomerRead(BaseModel):
    id: uuid.UUID
    name: str | None
    email: str | None
    phone: str | None
    gdpr_deleted_at: datetime | None

    model_config = {"from_attributes": True}
