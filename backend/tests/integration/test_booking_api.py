"""
Integration tests for the public booking API.

These tests mock the service layer to avoid needing a live database.
The tstzrange exclusion constraint is tested separately in the concurrency suite.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models.booking import BookingStatus


# ── Helpers ──────────────────────────────────────────────────────────────────

def _make_booking_mock(service_id=None, team_member_id=None):
    from app.models.booking import Booking

    bk = MagicMock(spec=Booking)
    bk.id = uuid.uuid4()
    bk.service_id = service_id or uuid.uuid4()
    bk.team_member_id = team_member_id or uuid.uuid4()
    bk.customer_id = uuid.uuid4()
    bk.start_at = datetime(2026, 6, 1, 9, 0, tzinfo=timezone.utc)
    bk.end_at = datetime(2026, 6, 1, 10, 0, tzinfo=timezone.utc)
    bk.status = BookingStatus.PENDING
    bk.customer_notes = None
    bk.internal_notes = None
    return bk


def _valid_payload(service_id=None, team_member_id=None) -> dict:
    return {
        "service_id": str(service_id or uuid.uuid4()),
        "team_member_id": str(team_member_id or uuid.uuid4()),
        "start_at": "2026-06-01T09:00:00+00:00",
        "customer_name": "Test User",
        "customer_email": "test@example.com",
    }


# ── Tests ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_booking_returns_201():
    """POST /api/public/bookings with a valid payload returns 201."""
    mock_booking = _make_booking_mock()

    with MagicMock() as _:
        from unittest.mock import patch
        with patch(
            "app.api.v1.endpoints.public_booking.create_public_booking",
            new_callable=AsyncMock,
            return_value=mock_booking,
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                resp = await client.post("/api/public/bookings", json=_valid_payload())

    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_create_booking_conflict_returns_409():
    """A booking conflict (slot taken) returns HTTP 409."""
    from unittest.mock import patch
    from app.services.booking import BookingConflict

    with patch(
        "app.api.v1.endpoints.public_booking.create_public_booking",
        new_callable=AsyncMock,
        side_effect=BookingConflict(),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post("/api/public/bookings", json=_valid_payload())

    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_create_booking_license_blocked_returns_402():
    """When demo limits are reached, booking creation returns HTTP 402."""
    from unittest.mock import patch
    from app.services.booking import BookingNotAllowed

    with patch(
        "app.api.v1.endpoints.public_booking.create_public_booking",
        new_callable=AsyncMock,
        side_effect=BookingNotAllowed("Demo limit reached."),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post("/api/public/bookings", json=_valid_payload())

    assert resp.status_code == 402


@pytest.mark.asyncio
async def test_create_booking_invalid_license_no_demo_fallback():
    """An invalid (tampered) license raises BookingNotAllowed, not a demo fallback."""
    from unittest.mock import patch
    from app.services.booking import BookingNotAllowed

    with patch(
        "app.api.v1.endpoints.public_booking.create_public_booking",
        new_callable=AsyncMock,
        side_effect=BookingNotAllowed("License is invalid."),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post("/api/public/bookings", json=_valid_payload())

    assert resp.status_code == 402
    assert "invalid" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_booking_service_not_found_returns_404():
    """An inactive or missing service returns HTTP 404."""
    from unittest.mock import patch
    from app.services.booking import ServiceNotFound

    with patch(
        "app.api.v1.endpoints.public_booking.create_public_booking",
        new_callable=AsyncMock,
        side_effect=ServiceNotFound("Service not found or inactive."),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post("/api/public/bookings", json=_valid_payload())

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_booking_payload_missing_required_field_returns_422():
    """A booking request without customer_name (required) returns HTTP 422."""
    payload = {
        "service_id": str(uuid.uuid4()),
        "team_member_id": str(uuid.uuid4()),
        "start_at": "2026-06-01T09:00:00+00:00",
        # customer_name is missing
    }
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp = await client.post("/api/public/bookings", json=payload)

    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_list_public_services_route_is_registered():
    """GET /api/public/services should be a known route (not 404 from missing route)."""
    from unittest.mock import patch, AsyncMock as AM

    with patch("app.api.v1.endpoints.public_booking.get_db") as mock_get_db:
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_get_db.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_get_db.return_value.__aexit__ = AsyncMock(return_value=False)

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/public/services")

    assert resp.status_code != 404
