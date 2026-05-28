import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDMixin


class NotificationType(str, enum.Enum):
    CONFIRMATION = "confirmation"
    REMINDER = "reminder"
    CANCELLATION = "cancellation"
    RESCHEDULE = "reschedule"


class NotificationChannel(str, enum.Enum):
    EMAIL = "email"


class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class Notification(Base, UUIDMixin):
    __tablename__ = "notifications"

    booking_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False
    )
    notification_type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType), nullable=False
    )
    channel: Mapped[NotificationChannel] = mapped_column(
        Enum(NotificationChannel), nullable=False, default=NotificationChannel.EMAIL
    )
    # Snapshot at send time — customer email may later be GDPR-nulled
    recipient_email: Mapped[str] = mapped_column(String(255), nullable=False)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[NotificationStatus] = mapped_column(
        Enum(NotificationStatus), nullable=False, default=NotificationStatus.PENDING
    )
    error_message: Mapped[str | None] = mapped_column(Text)

    booking: Mapped["Booking"] = relationship("Booking", back_populates="notifications")  # noqa: F821
