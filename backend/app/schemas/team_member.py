import uuid
from datetime import date, time
from pydantic import BaseModel, Field


class AvailabilityRuleCreate(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6)
    start_time: time
    end_time: time
    is_active: bool = True


class AvailabilityRuleRead(AvailabilityRuleCreate):
    id: uuid.UUID
    team_member_id: uuid.UUID

    model_config = {"from_attributes": True}


class AvailabilityExceptionCreate(BaseModel):
    exception_date: date
    is_blocked: bool = True
    start_time: time | None = None
    end_time: time | None = None
    note: str | None = None


class AvailabilityExceptionRead(AvailabilityExceptionCreate):
    id: uuid.UUID
    team_member_id: uuid.UUID

    model_config = {"from_attributes": True}


class TeamMemberBase(BaseModel):
    display_name: str = Field(..., min_length=1, max_length=255)
    email: str | None = None
    bio: str | None = None
    is_active: bool = True


class TeamMemberCreate(TeamMemberBase):
    service_ids: list[uuid.UUID] = []


class TeamMemberUpdate(BaseModel):
    display_name: str | None = Field(None, min_length=1, max_length=255)
    email: str | None = None
    bio: str | None = None
    is_active: bool | None = None
    service_ids: list[uuid.UUID] | None = None


class TeamMemberRead(TeamMemberBase):
    id: uuid.UUID
    user_id: uuid.UUID | None

    model_config = {"from_attributes": True}
