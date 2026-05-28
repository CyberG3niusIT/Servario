"""
Shared fixtures for Servario backend tests.

License fixtures use a test-only Ed25519 key pair generated at module load time.
These keys are NEVER used in production and are re-generated on each test run.
"""

import base64
import json
import uuid
from datetime import datetime, timedelta, timezone

import nacl.signing
import pytest


# ── Test key pair (generated fresh on import, not reused in production) ──────

@pytest.fixture(scope="session")
def test_signing_key() -> nacl.signing.SigningKey:
    return nacl.signing.SigningKey.generate()


@pytest.fixture(scope="session")
def test_verify_key(test_signing_key: nacl.signing.SigningKey) -> nacl.signing.VerifyKey:
    return test_signing_key.verify_key


# ── License document helpers ──────────────────────────────────────────────────

def _canonical(doc: dict) -> bytes:
    payload = {k: v for k, v in doc.items() if k != "signature"}
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()


def _sign(doc: dict, signing_key: nacl.signing.SigningKey) -> str:
    signed = signing_key.sign(_canonical(doc))
    return base64.b64encode(signed.signature).decode()


def make_license_doc(
    signing_key: nacl.signing.SigningKey,
    edition: str = "starter",
    max_staff: int = 5,
    max_services: int = -1,
    expires_at: datetime | None = None,
    grace_until: datetime | None = None,
    last_validated_at: datetime | None = None,
) -> dict:
    now = datetime.now(timezone.utc)
    doc = {
        "license_id": str(uuid.uuid4()),
        "customer_reference": "test-customer",
        "instance_id": str(uuid.uuid4()),
        "edition": edition,
        "allowed_features": [],
        "max_staff": max_staff,
        "max_services": max_services,
        "max_bookings_per_month": None,
        "issued_at": now.isoformat(),
        "expires_at": expires_at.isoformat() if expires_at else None,
        "last_validated_at": last_validated_at.isoformat() if last_validated_at else None,
        "grace_until": grace_until.isoformat() if grace_until else None,
    }
    doc["signature"] = _sign(doc, signing_key)
    return doc


def encode_license(doc: dict) -> str:
    return base64.b64encode(json.dumps(doc).encode()).decode()


@pytest.fixture
def valid_license_b64(test_signing_key):
    doc = make_license_doc(test_signing_key)
    return encode_license(doc)


@pytest.fixture
def expired_license_b64(test_signing_key):
    past = datetime.now(timezone.utc) - timedelta(days=60)
    doc = make_license_doc(test_signing_key, expires_at=past)
    return encode_license(doc)


@pytest.fixture
def expired_license_in_grace_b64(test_signing_key):
    past = datetime.now(timezone.utc) - timedelta(days=5)
    grace = datetime.now(timezone.utc) + timedelta(days=25)
    doc = make_license_doc(test_signing_key, expires_at=past, grace_until=grace)
    return encode_license(doc)
