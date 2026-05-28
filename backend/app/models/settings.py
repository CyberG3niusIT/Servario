from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class InstanceSettings(Base, TimestampMixin):
    """Single-row configuration for this Servario instance. id is always 1."""

    __tablename__ = "instance_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    business_name: Mapped[str | None] = mapped_column(String(255))
    business_email: Mapped[str | None] = mapped_column(String(255))
    business_phone: Mapped[str | None] = mapped_column(String(50))
    business_address: Mapped[str | None] = mapped_column(Text)
    booking_page_title: Mapped[str | None] = mapped_column(String(255))
    booking_page_description: Mapped[str | None] = mapped_column(Text)
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="UTC")
    smtp_host: Mapped[str | None] = mapped_column(String(255))
    smtp_port: Mapped[int | None] = mapped_column(Integer, default=587)
    smtp_user: Mapped[str | None] = mapped_column(String(255))
    smtp_password_encrypted: Mapped[str | None] = mapped_column(String(512))
