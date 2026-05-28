"""
Booking creation service.

Handles license/demo checks, creates the booking, and writes the audit entry.
The actual conflict prevention is enforced by the PostgreSQL tstzrange exclusion
constraint (migration 0002). If two concurrent requests try to create overlapping
bookings, the DB raises an IntegrityError which is caught and returned as HTTP 409.
"""

from __future__ import annotations

import uuid
from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.license import LicenseStatus, get_license_state
from app.models.booking import Booking, BookingStatus
from app.models.customer import Customer
from app.models.service import Service
from app.schemas.booking import PublicBookingCreate
from app.services import audit, notifications
from app.models.audit_log import AuditActorType


class BookingNotAllowed(Exception):
    def __init__(self, detail: str) -> None:
        self.detail = detail


class BookingConflict(Exception):
    pass


class ServiceNotFound(Exception):
    pass


async def _check_license_allows_booking(db: AsyncSession) -> None:
    state = get_license_state()

    if state.status == LicenseStatus.MISSING:
        # Count existing bookings to enforce demo limit
        count = await db.scalar(
            select(func.count()).select_from(Booking)
        )
        if (count or 0) >= state.DEMO_MAX_BOOKINGS:
            raise BookingNotAllowed(
                f"Demo mode limit reached ({state.DEMO_MAX_BOOKINGS} bookings). "
                "A valid license is required to create new bookings."
            )
    elif not state.bookings_allowed:
        if state.status == LicenseStatus.INVALID:
            raise BookingNotAllowed("License is invalid. Please provide a valid license key.")
        raise BookingNotAllowed("A valid license is required. Please check your license status.")


async def create_public_booking(
    db: AsyncSession,
    data: PublicBookingCreate,
) -> Booking:
    await _check_license_allows_booking(db)

    # Load service to determine end_at
    service = await db.get(Service, data.service_id)
    if not service or not service.is_active:
        raise ServiceNotFound("Service not found or inactive.")

    end_at = data.start_at + timedelta(minutes=service.duration_minutes)

    # Get or create customer
    customer = Customer(
        name=data.customer_name,
        email=data.customer_email,
        phone=data.customer_phone,
        notes=data.customer_notes,
    )
    db.add(customer)
    await db.flush()  # get customer.id before creating booking

    booking = Booking(
        service_id=data.service_id,
        team_member_id=data.team_member_id,
        customer_id=customer.id,
        start_at=data.start_at,
        end_at=end_at,
        status=BookingStatus.PENDING,
        customer_notes=data.customer_notes,
    )
    db.add(booking)

    try:
        await db.flush()  # triggers the exclusion constraint
    except IntegrityError as exc:
        await db.rollback()
        if "no_overlapping_bookings" in str(exc.orig):
            raise BookingConflict() from exc
        raise

    await audit.log(
        db=db,
        action="booking.created",
        entity_type="booking",
        entity_id=booking.id,
        actor_type=AuditActorType.PUBLIC,
    )

    await db.commit()

    # Reload with relationships for notification rendering
    result = await db.execute(
        select(Booking)
        .options(
            selectinload(Booking.service),
            selectinload(Booking.team_member),
            selectinload(Booking.customer),
        )
        .where(Booking.id == booking.id)
    )
    booking = result.scalar_one()

    # Bestätigungs-E-Mail asynchron versenden (Fehler werden geloggt, nicht weitergeworfen)
    try:
        await notifications.send_confirmation(db, booking)
        await db.commit()
    except Exception:
        pass

    return booking
