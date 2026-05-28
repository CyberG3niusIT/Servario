import enum
import uuid

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.db.base import Base, TimestampMixin, UUIDMixin


class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    COMPLETED = "completed"


class Booking(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "bookings"

    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("services.id"), nullable=False
    )
    team_member_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("team_members.id"), nullable=False, index=True
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False
    )
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus), nullable=False, default=BookingStatus.PENDING
    )
    customer_notes: Mapped[str | None] = mapped_column(Text)
    internal_notes: Mapped[str | None] = mapped_column(Text)

    service: Mapped["Service"] = relationship("Service", back_populates="bookings")  # noqa: F821
    team_member: Mapped["TeamMember"] = relationship("TeamMember", back_populates="bookings")  # noqa: F821
    customer: Mapped["Customer"] = relationship("Customer", back_populates="bookings")  # noqa: F821
    notifications: Mapped[list["Notification"]] = relationship(  # noqa: F821
        "Notification", back_populates="booking", cascade="all, delete-orphan"
    )

    # The tstzrange exclusion constraint is added via Alembic migration,
    # not here — SQLAlchemy ORM does not natively support EXCLUDE USING gist.
    # See: alembic/versions/0002_add_booking_overlap_constraint.py
