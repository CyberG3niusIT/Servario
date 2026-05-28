"""Initial schema

Revision ID: 0001
Revises:
Create Date: 2026-05-28
"""

from typing import Sequence, Union
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "instance_settings",
        sa.Column("id", sa.Integer(), primary_key=True, default=1),
        sa.Column("business_name", sa.String(255), nullable=True),
        sa.Column("business_email", sa.String(255), nullable=True),
        sa.Column("business_phone", sa.String(50), nullable=True),
        sa.Column("business_address", sa.Text(), nullable=True),
        sa.Column("booking_page_title", sa.String(255), nullable=True),
        sa.Column("booking_page_description", sa.Text(), nullable=True),
        sa.Column("timezone", sa.String(64), nullable=False, server_default="UTC"),
        sa.Column("smtp_host", sa.String(255), nullable=True),
        sa.Column("smtp_port", sa.Integer(), nullable=True, server_default="587"),
        sa.Column("smtp_user", sa.String(255), nullable=True),
        sa.Column("smtp_password_encrypted", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=True),
        sa.Column(
            "role",
            sa.Enum("owner", "admin", "staff", name="userrole"),
            nullable=False,
            server_default="staff",
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "team_members",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "availability_rules",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("team_member_id", UUID(as_uuid=True), sa.ForeignKey("team_members.id", ondelete="CASCADE"), nullable=False),
        sa.Column("day_of_week", sa.SmallInteger(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
    )

    op.create_table(
        "availability_exceptions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("team_member_id", UUID(as_uuid=True), sa.ForeignKey("team_members.id", ondelete="CASCADE"), nullable=False),
        sa.Column("exception_date", sa.Date(), nullable=False),
        sa.Column("is_blocked", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("start_time", sa.Time(), nullable=True),
        sa.Column("end_time", sa.Time(), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
    )

    op.create_table(
        "services",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=True),
        sa.Column("currency", sa.String(3), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "service_team_members",
        sa.Column("service_id", UUID(as_uuid=True), sa.ForeignKey("services.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("team_member_id", UUID(as_uuid=True), sa.ForeignKey("team_members.id", ondelete="CASCADE"), primary_key=True),
    )

    op.create_table(
        "customers",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("gdpr_deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "bookings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("service_id", UUID(as_uuid=True), sa.ForeignKey("services.id"), nullable=False),
        sa.Column("team_member_id", UUID(as_uuid=True), sa.ForeignKey("team_members.id"), nullable=False),
        sa.Column("customer_id", UUID(as_uuid=True), sa.ForeignKey("customers.id"), nullable=False),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "confirmed", "cancelled", "no_show", "completed", name="bookingstatus"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("customer_notes", sa.Text(), nullable=True),
        sa.Column("internal_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_bookings_team_member_id", "bookings", ["team_member_id"])

    op.create_table(
        "notifications",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("booking_id", UUID(as_uuid=True), sa.ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "notification_type",
            sa.Enum("confirmation", "reminder", "cancellation", "reschedule", name="notificationtype"),
            nullable=False,
        ),
        sa.Column(
            "channel",
            sa.Enum("email", name="notificationchannel"),
            nullable=False,
            server_default="email",
        ),
        sa.Column("recipient_email", sa.String(255), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "status",
            sa.Enum("pending", "sent", "failed", name="notificationstatus"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("error_message", sa.Text(), nullable=True),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "actor_type",
            sa.Enum("user", "system", "public", name="auditactortype"),
            nullable=False,
        ),
        sa.Column("actor_id", UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(128), nullable=False),
        sa.Column("entity_type", sa.String(64), nullable=False),
        sa.Column("entity_id", UUID(as_uuid=True), nullable=True),
        sa.Column("changes_json", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("notifications")
    op.drop_table("bookings")
    op.drop_table("customers")
    op.drop_table("service_team_members")
    op.drop_table("services")
    op.drop_table("availability_exceptions")
    op.drop_table("availability_rules")
    op.drop_table("team_members")
    op.drop_table("users")
    op.drop_table("instance_settings")
    op.execute("DROP TYPE IF EXISTS userrole")
    op.execute("DROP TYPE IF EXISTS bookingstatus")
    op.execute("DROP TYPE IF EXISTS notificationtype")
    op.execute("DROP TYPE IF EXISTS notificationchannel")
    op.execute("DROP TYPE IF EXISTS notificationstatus")
    op.execute("DROP TYPE IF EXISTS auditactortype")
