"""
Concurrency test: simultaneous booking attempts for the same slot.

This test spins up two concurrent coroutines that each try to create a booking
for the exact same team_member + time window. The PostgreSQL tstzrange exclusion
constraint guarantees exactly one succeeds and the other receives an IntegrityError
(surfaced as BookingConflict by the service layer).

Requires a real PostgreSQL database. Skipped automatically in environments where
DATABASE_URL points to SQLite or is not set.
"""
from __future__ import annotations

import asyncio
import os
import uuid
from datetime import datetime, timedelta, timezone

import pytest


pytestmark = pytest.mark.skipif(
    not os.environ.get("DATABASE_URL", "").startswith("postgresql"),
    reason="Concurrency test requires a real PostgreSQL database",
)


@pytest.fixture
async def db_session():
    """Provide a real async session; skip if no PostgreSQL DATABASE_URL."""
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from sqlalchemy.orm import sessionmaker

    url = os.environ["DATABASE_URL"]
    engine = create_async_engine(url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
    await engine.dispose()


@pytest.fixture
async def seeded_service_and_member(db_session):
    """Insert minimal service + team member rows for the race test."""
    from app.models.service import Service, ServiceTeamMember
    from app.models.team_member import TeamMember

    svc = Service(
        name="Race Test Service",
        duration_minutes=60,
        is_active=True,
        description=None,
        price_cents=None,
        currency=None,
        color=None,
    )
    db_session.add(svc)
    await db_session.flush()

    member = TeamMember(display_name="Race Tester", is_active=True)
    db_session.add(member)
    await db_session.flush()

    db_session.add(ServiceTeamMember(service_id=svc.id, team_member_id=member.id))
    await db_session.commit()

    yield svc, member

    # Teardown: delete test rows (cascade handles bookings/customers)
    await db_session.delete(member)
    await db_session.delete(svc)
    await db_session.commit()


@pytest.mark.asyncio
async def test_concurrent_booking_only_one_succeeds(seeded_service_and_member):
    """
    Two concurrent create_public_booking calls for the same slot must result in
    exactly one success (HTTP 201) and one conflict (BookingConflict / HTTP 409).
    The tstzrange exclusion constraint is the enforcement mechanism.
    """
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from sqlalchemy.orm import sessionmaker

    from app.schemas.booking import PublicBookingCreate
    from app.services.booking import BookingConflict, create_public_booking

    svc, member = seeded_service_and_member
    url = os.environ["DATABASE_URL"]
    engine = create_async_engine(url, echo=False)
    async_session_factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    start_at = datetime(2026, 7, 1, 10, 0, tzinfo=timezone.utc)
    payload = PublicBookingCreate(
        service_id=svc.id,
        team_member_id=member.id,
        start_at=start_at,
        customer_name="Race Customer",
        customer_email="race@example.com",
        customer_phone=None,
        customer_notes=None,
    )

    results: list[str] = []

    async def attempt():
        async with async_session_factory() as session:
            try:
                await create_public_booking(session, payload)
                results.append("success")
            except BookingConflict:
                results.append("conflict")

    await asyncio.gather(attempt(), attempt())

    await engine.dispose()

    assert sorted(results) == ["conflict", "success"], (
        f"Expected exactly one success and one conflict, got: {results}"
    )
