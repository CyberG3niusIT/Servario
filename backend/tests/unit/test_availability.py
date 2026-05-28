"""Unit tests for the availability slot calculation engine."""
from datetime import date, time, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.availability import get_available_slots


def _make_rule(day_of_week: int, start: str, end: str):
    rule = MagicMock()
    rule.day_of_week = day_of_week
    rule.start_time = time.fromisoformat(start)
    rule.end_time = time.fromisoformat(end)
    rule.is_active = True
    return rule


def _make_exception(ex_date: date, is_blocked: bool, start=None, end=None):
    exc = MagicMock()
    exc.exception_date = ex_date
    exc.is_blocked = is_blocked
    exc.start_time = time.fromisoformat(start) if start else None
    exc.end_time = time.fromisoformat(end) if end else None
    return exc


def _make_booking(start_str: str, end_str: str):
    from datetime import datetime

    bk = MagicMock()
    bk.start_at = datetime.fromisoformat(start_str).replace(tzinfo=timezone.utc)
    bk.end_at = datetime.fromisoformat(end_str).replace(tzinfo=timezone.utc)
    return bk


@pytest.fixture
def mock_db():
    return AsyncMock()


def _patch_db_queries(mock_db, *, rules, exceptions, bookings):
    results = []
    for items in (rules, exceptions, bookings):
        result = MagicMock()
        result.scalars.return_value.all.return_value = items
        results.append(result)
    mock_db.execute.side_effect = results


@pytest.mark.asyncio
async def test_no_rule_for_requested_day_returns_empty(mock_db):
    """If there is no availability rule for the requested day, return []."""
    import uuid

    # Monday = 0; requesting a Thursday = 3 with only Monday rule
    monday_rule = _make_rule(day_of_week=0, start="09:00", end="17:00")
    _patch_db_queries(mock_db, rules=[monday_rule], exceptions=[], bookings=[])

    slots = await get_available_slots(
        db=mock_db,
        team_member_id=uuid.uuid4(),
        duration_minutes=60,
        requested_date=date(2026, 1, 1),  # Thursday
        business_timezone="UTC",
    )
    assert slots == []


@pytest.mark.asyncio
async def test_basic_slots_generated_correctly(mock_db):
    """09:00–11:00 window with 60-min slots should yield 09:00 and 10:00."""
    import uuid

    thursday = date(2026, 1, 1)  # Thursday = weekday 3
    rule = _make_rule(day_of_week=3, start="09:00", end="11:00")
    _patch_db_queries(mock_db, rules=[rule], exceptions=[], bookings=[])

    slots = await get_available_slots(
        db=mock_db,
        team_member_id=uuid.uuid4(),
        duration_minutes=60,
        requested_date=thursday,
        business_timezone="UTC",
    )
    assert len(slots) == 2
    assert slots[0].start_at.hour == 9
    assert slots[1].start_at.hour == 10


@pytest.mark.asyncio
async def test_exception_closed_day_returns_empty(mock_db):
    """An is_blocked=True exception on a normally-open day returns no slots."""
    import uuid

    thursday = date(2026, 1, 1)
    rule = _make_rule(day_of_week=3, start="09:00", end="17:00")
    exc = _make_exception(ex_date=thursday, is_blocked=True)
    _patch_db_queries(mock_db, rules=[rule], exceptions=[exc], bookings=[])

    slots = await get_available_slots(
        db=mock_db,
        team_member_id=uuid.uuid4(),
        duration_minutes=60,
        requested_date=thursday,
        business_timezone="UTC",
    )
    assert slots == []


@pytest.mark.asyncio
async def test_exception_custom_hours_overrides_rule(mock_db):
    """An exception with custom hours replaces the rule's hours."""
    import uuid

    thursday = date(2026, 1, 1)
    rule = _make_rule(day_of_week=3, start="09:00", end="17:00")
    exc = _make_exception(ex_date=thursday, is_blocked=False, start="13:00", end="15:00")
    _patch_db_queries(mock_db, rules=[rule], exceptions=[exc], bookings=[])

    slots = await get_available_slots(
        db=mock_db,
        team_member_id=uuid.uuid4(),
        duration_minutes=60,
        requested_date=thursday,
        business_timezone="UTC",
    )
    assert len(slots) == 2
    assert slots[0].start_at.hour == 13
    assert slots[1].start_at.hour == 14


@pytest.mark.asyncio
async def test_conflicting_booking_removed_from_slots(mock_db):
    """A slot occupied by an existing booking must not appear in results."""
    import uuid

    thursday = date(2026, 1, 1)
    rule = _make_rule(day_of_week=3, start="09:00", end="11:00")
    booking = _make_booking("2026-01-01T09:00:00", "2026-01-01T10:00:00")
    _patch_db_queries(mock_db, rules=[rule], exceptions=[], bookings=[booking])

    slots = await get_available_slots(
        db=mock_db,
        team_member_id=uuid.uuid4(),
        duration_minutes=60,
        requested_date=thursday,
        business_timezone="UTC",
    )
    assert len(slots) == 1
    assert slots[0].start_at.hour == 10


@pytest.mark.asyncio
async def test_partial_overlap_booking_removes_slot(mock_db):
    """A booking that partially overlaps a slot still blocks it."""
    import uuid

    thursday = date(2026, 1, 1)
    rule = _make_rule(day_of_week=3, start="09:00", end="11:00")
    # Booking from 09:30–10:30 blocks both 09:00 and 10:00 slots (60 min each)
    booking = _make_booking("2026-01-01T09:30:00", "2026-01-01T10:30:00")
    _patch_db_queries(mock_db, rules=[rule], exceptions=[], bookings=[booking])

    slots = await get_available_slots(
        db=mock_db,
        team_member_id=uuid.uuid4(),
        duration_minutes=60,
        requested_date=thursday,
        business_timezone="UTC",
    )
    assert slots == []


@pytest.mark.asyncio
async def test_30_min_slots_in_one_hour_window(mock_db):
    """A 60-minute window with 30-min duration should yield exactly 2 slots."""
    import uuid

    thursday = date(2026, 1, 1)
    rule = _make_rule(day_of_week=3, start="09:00", end="10:00")
    _patch_db_queries(mock_db, rules=[rule], exceptions=[], bookings=[])

    slots = await get_available_slots(
        db=mock_db,
        team_member_id=uuid.uuid4(),
        duration_minutes=30,
        requested_date=thursday,
        business_timezone="UTC",
    )
    assert len(slots) == 2
    assert slots[0].start_at.minute == 0
    assert slots[1].start_at.minute == 30
