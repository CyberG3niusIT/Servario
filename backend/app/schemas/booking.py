import uuid
from datetime import datetime
from pydantic import BaseModel, Field

from app.models.booking import BookingStatus


class PublicBookingCreate(BaseModel):
    """Used by the public booking page — no auth required."""
    service_id: uuid.UUID
    team_member_id: uuid.UUID
    start_at: datetime
    customer_name: str = Field(..., min_length=1, max_length=255)
    customer_email: str | None = None
    customer_phone: str | None = None
    customer_notes: str | None = None


class BookingRead(BaseModel):
    id: uuid.UUID
    service_id: uuid.UUID
    team_member_id: uuid.UUID
    customer_id: uuid.UUID
    start_at: datetime
    end_at: datetime
    status: BookingStatus
    customer_notes: str | None
    internal_notes: str | None

    model_config = {"from_attributes": True}


class BookingAdminUpdate(BaseModel):
    internal_notes: str | None = None
    status: BookingStatus | None = None


class AvailabilitySlot(BaseModel):
    start_at: datetime
    end_at: datetime
