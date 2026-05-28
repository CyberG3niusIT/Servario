import uuid
from datetime import date, time

from sqlalchemy import Boolean, Date, ForeignKey, SmallInteger, Text, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDMixin


class AvailabilityRule(Base, UUIDMixin):
    """Recurring weekly availability for a TeamMember."""

    __tablename__ = "availability_rules"

    team_member_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("team_members.id", ondelete="CASCADE"), nullable=False
    )
    day_of_week: Mapped[int] = mapped_column(
        SmallInteger, nullable=False
    )  # 0=Monday … 6=Sunday
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    team_member: Mapped["TeamMember"] = relationship(  # noqa: F821
        "TeamMember", back_populates="availability_rules"
    )


class AvailabilityException(Base, UUIDMixin):
    """One-off override (blocked day or special hours) for a TeamMember."""

    __tablename__ = "availability_exceptions"

    team_member_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("team_members.id", ondelete="CASCADE"), nullable=False
    )
    exception_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_blocked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    start_time: Mapped[time | None] = mapped_column(Time)
    end_time: Mapped[time | None] = mapped_column(Time)
    note: Mapped[str | None] = mapped_column(Text)

    team_member: Mapped["TeamMember"] = relationship(  # noqa: F821
        "TeamMember", back_populates="availability_exceptions"
    )
