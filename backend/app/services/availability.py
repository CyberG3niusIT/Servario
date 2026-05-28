"""
Scheduling engine: compute available time slots for a team member on a given date.

Algorithm:
  1. Find AvailabilityRules for the team member matching the day of week.
  2. Apply any AvailabilityExceptions for that specific date (block or override).
  3. Divide each availability window into slots of `duration_minutes`.
  4. Remove slots that overlap with existing pending/confirmed bookings.
  5. Remove slots in the past.

All datetimes are timezone-aware (UTC internally; converted from business timezone).
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.availability import AvailabilityException, AvailabilityRule
from app.models.booking import Booking, BookingStatus
from app.schemas.booking import AvailabilitySlot


def _tz(tz_name: str) -> ZoneInfo:
    try:
        return ZoneInfo(tz_name)
    except (ZoneInfoNotFoundError, KeyError):
        return ZoneInfo("UTC")


async def get_available_slots(
    db: AsyncSession,
    team_member_id: uuid.UUID,
    duration_minutes: int,
    requested_date: date,
    business_timezone: str = "UTC",
) -> list[AvailabilitySlot]:
    tz = _tz(business_timezone)
    day_of_week = requested_date.weekday()  # 0=Monday … 6=Sunday

    # ── 1. Load availability rules for this day ───────────────────────────────
    rules_result = await db.execute(
        select(AvailabilityRule).where(
            and_(
                AvailabilityRule.team_member_id == team_member_id,
                AvailabilityRule.day_of_week == day_of_week,
                AvailabilityRule.is_active.is_(True),
            )
        )
    )
    rules = rules_result.scalars().all()

    # ── 2. Check for exceptions on this date ──────────────────────────────────
    exc_result = await db.execute(
        select(AvailabilityException).where(
            and_(
                AvailabilityException.team_member_id == team_member_id,
                AvailabilityException.exception_date == requested_date,
            )
        )
    )
    exceptions = exc_result.scalars().all()

    # Determine effective windows for the day
    windows: list[tuple[datetime, datetime]] = []

    if exceptions:
        for exc in exceptions:
            if exc.is_blocked:
                return []  # entire day blocked
            if exc.start_time and exc.end_time:
                start_dt = datetime.combine(requested_date, exc.start_time, tzinfo=tz)
                end_dt = datetime.combine(requested_date, exc.end_time, tzinfo=tz)
                windows.append((start_dt, end_dt))
    else:
        for rule in rules:
            start_dt = datetime.combine(requested_date, rule.start_time, tzinfo=tz)
            end_dt = datetime.combine(requested_date, rule.end_time, tzinfo=tz)
            windows.append((start_dt, end_dt))

    if not windows:
        return []

    # ── 3. Generate candidate slots ───────────────────────────────────────────
    duration = timedelta(minutes=duration_minutes)
    now = datetime.now(timezone.utc)
    candidates: list[tuple[datetime, datetime]] = []

    for window_start, window_end in windows:
        slot_start = window_start
        while slot_start + duration <= window_end:
            slot_end = slot_start + duration
            # Skip slots in the past
            if slot_end.astimezone(timezone.utc) > now:
                candidates.append((
                    slot_start.astimezone(timezone.utc),
                    slot_end.astimezone(timezone.utc),
                ))
            slot_start += duration

    if not candidates:
        return []

    # ── 4. Load existing bookings for this team member on this date ───────────
    day_start = datetime.combine(requested_date, datetime.min.time(), tzinfo=tz).astimezone(timezone.utc)
    day_end = datetime.combine(requested_date, datetime.max.time(), tzinfo=tz).astimezone(timezone.utc)

    bookings_result = await db.execute(
        select(Booking).where(
            and_(
                Booking.team_member_id == team_member_id,
                Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
                Booking.start_at < day_end,
                Booking.end_at > day_start,
            )
        )
    )
    existing = bookings_result.scalars().all()

    # ── 5. Remove conflicting candidates ─────────────────────────────────────
    available: list[AvailabilitySlot] = []
    for slot_start, slot_end in candidates:
        conflicts = any(
            b.start_at < slot_end and b.end_at > slot_start
            for b in existing
        )
        if not conflicts:
            available.append(AvailabilitySlot(start_at=slot_start, end_at=slot_end))

    return available
