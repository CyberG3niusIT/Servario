from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.db.base import Base, TimestampMixin, UUIDMixin


class Customer(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "customers"

    name: Mapped[str | None] = mapped_column(String(255))
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(50))
    notes: Mapped[str | None] = mapped_column(Text)
    # Set when GDPR erasure is fulfilled; personal fields above are nulled
    gdpr_deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    bookings: Mapped[list["Booking"]] = relationship("Booking", back_populates="customer")  # noqa: F821
