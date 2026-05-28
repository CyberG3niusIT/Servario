import uuid

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class TeamMember(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "team_members"

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255))
    bio: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    user: Mapped["User | None"] = relationship("User", back_populates="team_member")  # noqa: F821
    availability_rules: Mapped[list["AvailabilityRule"]] = relationship(  # noqa: F821
        "AvailabilityRule", back_populates="team_member", cascade="all, delete-orphan"
    )
    availability_exceptions: Mapped[list["AvailabilityException"]] = relationship(  # noqa: F821
        "AvailabilityException", back_populates="team_member", cascade="all, delete-orphan"
    )
    service_assignments: Mapped[list["ServiceTeamMember"]] = relationship(  # noqa: F821
        "ServiceTeamMember", back_populates="team_member", cascade="all, delete-orphan"
    )
    bookings: Mapped[list["Booking"]] = relationship(  # noqa: F821
        "Booking", back_populates="team_member"
    )
