import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class Service(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "services"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float | None] = mapped_column(Numeric(10, 2))
    currency: Mapped[str | None] = mapped_column(String(3))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    team_member_assignments: Mapped[list["ServiceTeamMember"]] = relationship(  # noqa: F821
        "ServiceTeamMember", back_populates="service", cascade="all, delete-orphan"
    )
    bookings: Mapped[list["Booking"]] = relationship("Booking", back_populates="service")  # noqa: F821


class ServiceTeamMember(Base):
    """N:M junction: which TeamMembers offer which Services."""

    __tablename__ = "service_team_members"

    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("services.id", ondelete="CASCADE"), primary_key=True
    )
    team_member_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("team_members.id", ondelete="CASCADE"),
        primary_key=True,
    )

    service: Mapped["Service"] = relationship("Service", back_populates="team_member_assignments")
    team_member: Mapped["TeamMember"] = relationship(  # noqa: F821
        "TeamMember", back_populates="service_assignments"
    )
