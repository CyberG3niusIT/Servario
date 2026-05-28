"""
Unit tests for the license validation module.

These tests use a test-only Ed25519 key pair and do not touch the database
or the production public key.
"""

import base64
import json
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import nacl.signing
import pytest

from app.core.license import (
    LicenseStatus,
    validate_license_from_env,
)
from tests.conftest import encode_license, make_license_doc


# ── Missing license ───────────────────────────────────────────────────────────

def test_missing_license_returns_missing_status():
    state = validate_license_from_env("")
    assert state.status == LicenseStatus.MISSING


def test_missing_license_allows_bookings_when_demo_limits_not_reached():
    state = validate_license_from_env("")
    assert state.bookings_allowed is True


def test_missing_license_blocks_bookings_when_demo_booking_limit_reached():
    state = validate_license_from_env("")
    state.demo_booking_count = 5
    assert state.bookings_allowed is False


def test_missing_license_blocks_bookings_when_demo_staff_limit_reached():
    state = validate_license_from_env("")
    state.demo_staff_count = 2
    assert state.bookings_allowed is False


def test_missing_license_blocks_bookings_after_demo_window():
    from datetime import timezone
    state = validate_license_from_env("")
    state.demo_started_at = datetime.now(timezone.utc) - timedelta(days=31)
    assert state.bookings_allowed is False


# ── Invalid license (NO demo fallback) ───────────────────────────────────────

def test_tampered_license_returns_invalid():
    key = nacl.signing.SigningKey.generate()
    doc = make_license_doc(key)
    doc["max_staff"] = 9999  # tamper after signing
    state = validate_license_from_env(encode_license(doc))
    assert state.status == LicenseStatus.INVALID


def test_invalid_license_blocks_bookings():
    state = validate_license_from_env("not-valid-base64!!!")
    assert state.status == LicenseStatus.INVALID
    assert state.bookings_allowed is False


def test_invalid_license_has_no_demo_fallback():
    """Critical: invalid ≠ missing. An invalid license must not activate demo mode."""
    state = validate_license_from_env("bm90LXZhbGlk")  # base64 of "not-valid"
    assert state.status == LicenseStatus.INVALID
    # bookings_allowed must be False regardless of demo counters
    state.demo_booking_count = 0
    assert state.bookings_allowed is False


# ── Valid license ─────────────────────────────────────────────────────────────

def test_valid_license_returns_active(test_signing_key):
    doc = make_license_doc(test_signing_key)
    with patch("app.core.license._PUBLIC_KEY_B64",
               base64.b64encode(bytes(test_signing_key.verify_key)).decode()):
        state = validate_license_from_env(encode_license(doc))
    assert state.status == LicenseStatus.ACTIVE
    assert state.bookings_allowed is True


# ── Expired license ───────────────────────────────────────────────────────────

def test_expired_license_outside_grace_returns_expired(test_signing_key):
    past = datetime.now(timezone.utc) - timedelta(days=60)
    doc = make_license_doc(test_signing_key, expires_at=past)
    with patch("app.core.license._PUBLIC_KEY_B64",
               base64.b64encode(bytes(test_signing_key.verify_key)).decode()):
        state = validate_license_from_env(encode_license(doc))
    assert state.status == LicenseStatus.EXPIRED
    assert state.bookings_allowed is False


def test_expired_license_within_grace_returns_grace(test_signing_key):
    past = datetime.now(timezone.utc) - timedelta(days=2)
    grace = datetime.now(timezone.utc) + timedelta(days=28)
    doc = make_license_doc(test_signing_key, expires_at=past, grace_until=grace)
    with patch("app.core.license._PUBLIC_KEY_B64",
               base64.b64encode(bytes(test_signing_key.verify_key)).decode()):
        state = validate_license_from_env(encode_license(doc))
    assert state.status == LicenseStatus.GRACE
    assert state.bookings_allowed is True


# ── License limits ────────────────────────────────────────────────────────────

def test_staff_limit_enforced_in_demo():
    state = validate_license_from_env("")
    assert state.check_staff_limit(0) is True
    assert state.check_staff_limit(1) is True
    assert state.check_staff_limit(2) is False  # max is 2


def test_service_limit_enforced_in_demo():
    state = validate_license_from_env("")
    assert state.check_service_limit(2) is True
    assert state.check_service_limit(3) is False  # max is 3


def test_unlimited_staff_with_valid_license(test_signing_key):
    doc = make_license_doc(test_signing_key, max_staff=-1)
    with patch("app.core.license._PUBLIC_KEY_B64",
               base64.b64encode(bytes(test_signing_key.verify_key)).decode()):
        state = validate_license_from_env(encode_license(doc))
    assert state.check_staff_limit(9999) is True
