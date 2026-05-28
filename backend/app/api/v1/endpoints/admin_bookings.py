import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps.auth import get_current_user
from app.db.session import get_db
from app.models.booking import Booking, BookingStatus
from app.models.user import User
from app.schemas.booking import BookingAdminUpdate, BookingRead
from app.services import audit, notifications
from app.models.audit_log import AuditActorType

router = APIRouter(prefix="/api/admin/bookings", tags=["admin-bookings"])


@router.get("", response_model=list[BookingRead])
async def list_bookings(
    status_filter: BookingStatus | None = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Booking]:
    q = select(Booking).order_by(Booking.start_at.desc())
    if status_filter:
        q = q.where(Booking.status == status_filter)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/{booking_id}", response_model=BookingRead)
async def get_booking(
    booking_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Booking:
    booking = await db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")
    return booking


@router.patch("/{booking_id}", response_model=BookingRead)
async def update_booking(
    booking_id: uuid.UUID,
    data: BookingAdminUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Booking:
    booking = await db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")

    old_status = booking.status
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(booking, field, value)

    await audit.log(
        db=db,
        action="booking.updated",
        entity_type="booking",
        entity_id=booking.id,
        actor_type=AuditActorType.USER,
        actor_id=current_user.id,
        changes={"status": {"from": old_status, "to": booking.status}} if data.status else None,
    )

    await db.commit()
    await db.refresh(booking)
    return booking


@router.post("/{booking_id}/confirm", response_model=BookingRead)
async def confirm_booking(
    booking_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Booking:
    booking = await db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")
    if booking.status != BookingStatus.PENDING:
        raise HTTPException(status_code=400, detail=f"Cannot confirm a booking with status '{booking.status}'.")

    booking.status = BookingStatus.CONFIRMED
    await audit.log(
        db=db,
        action="booking.confirmed",
        entity_type="booking",
        entity_id=booking.id,
        actor_type=AuditActorType.USER,
        actor_id=current_user.id,
    )
    await db.commit()
    await db.refresh(booking)
    return booking


@router.post("/{booking_id}/cancel", response_model=BookingRead)
async def cancel_booking(
    booking_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Booking:
    booking = await db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")
    if booking.status in (BookingStatus.CANCELLED, BookingStatus.COMPLETED):
        raise HTTPException(status_code=400, detail=f"Cannot cancel a booking with status '{booking.status}'.")

    booking.status = BookingStatus.CANCELLED
    await audit.log(
        db=db,
        action="booking.cancelled",
        entity_type="booking",
        entity_id=booking.id,
        actor_type=AuditActorType.USER,
        actor_id=current_user.id,
    )
    await db.commit()

    # Absage-E-Mail versenden
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
    try:
        await notifications.send_cancellation(db, booking)
        await db.commit()
    except Exception:
        pass

    return booking
