from datetime import date

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.service import Service, ServiceTeamMember
from app.models.team_member import TeamMember
from app.schemas.booking import AvailabilitySlot, BookingRead, PublicBookingCreate
from app.schemas.service import ServiceRead
from app.schemas.team_member import TeamMemberRead
from app.services.availability import get_available_slots
from app.services.booking import (
    BookingConflict,
    BookingNotAllowed,
    ServiceNotFound,
    create_public_booking,
)

router = APIRouter(prefix="/api/public", tags=["public"])


@router.get("/services", response_model=list[ServiceRead])
async def list_public_services(db: AsyncSession = Depends(get_db)) -> list[Service]:
    result = await db.execute(
        select(Service).where(Service.is_active.is_(True)).order_by(Service.name)
    )
    return result.scalars().all()


@router.get("/services/{service_id}/team-members", response_model=list[TeamMemberRead])
async def list_service_team_members(
    service_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list[TeamMember]:
    result = await db.execute(
        select(TeamMember)
        .join(ServiceTeamMember, ServiceTeamMember.team_member_id == TeamMember.id)
        .where(
            and_(
                ServiceTeamMember.service_id == service_id,
                TeamMember.is_active.is_(True),
            )
        )
        .order_by(TeamMember.display_name)
    )
    return result.scalars().all()


@router.get("/availability", response_model=list[AvailabilitySlot])
async def get_availability(
    service_id: uuid.UUID = Query(...),
    team_member_id: uuid.UUID = Query(...),
    date: date = Query(...),
    db: AsyncSession = Depends(get_db),
) -> list[AvailabilitySlot]:
    service = await db.get(Service, service_id)
    if not service or not service.is_active:
        raise HTTPException(status_code=404, detail="Service not found.")

    # TODO: read timezone from InstanceSettings (hardcoded UTC for MVP)
    return await get_available_slots(
        db=db,
        team_member_id=team_member_id,
        duration_minutes=service.duration_minutes,
        requested_date=date,
        business_timezone="UTC",
    )


@router.post("/bookings", response_model=BookingRead, status_code=status.HTTP_201_CREATED)
async def create_booking(
    data: PublicBookingCreate,
    db: AsyncSession = Depends(get_db),
) -> BookingRead:
    try:
        booking = await create_public_booking(db, data)
    except BookingNotAllowed as exc:
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=exc.detail)
    except BookingConflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This time slot is no longer available. Please choose another time.",
        )
    except ServiceNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return booking


@router.get("/bookings/{booking_id}", response_model=BookingRead)
async def get_booking(
    booking_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> BookingRead:
    from app.models.booking import Booking
    booking = await db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")
    return booking
