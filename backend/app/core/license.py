"""
License validation module.

Validates Ed25519-signed license documents. The private key lives exclusively
on the License Broker (private vendor system). This module only holds the
public key for signature verification.

Status semantics:
  missing  – no license configured; Demo/Eval mode allowed until hard limits
  invalid  – license present but signature or structure is wrong; NO demo fallback
  active   – license valid, within expiry, online validation current
  expired  – expires_at in the past AND grace period elapsed
  grace    – online validation unavailable but within grace window
  revoked  – license marked revoked by the broker
  server_unreachable – technical intermediate; treated as grace if within window
"""

from __future__ import annotations

import base64
import json
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

import nacl.signing
import nacl.exceptions


# ---------------------------------------------------------------------------
# Public key (Ed25519 verify key)
# Replace with the real production public key before first release.
# This is a placeholder key that will reject all license documents.
# ---------------------------------------------------------------------------
_PUBLIC_KEY_B64: str = os.environ.get(
    "SERVARIO_LICENSE_PUBLIC_KEY",
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",  # placeholder – always invalid
)


class LicenseStatus(str, Enum):
    MISSING = "missing"
    INVALID = "invalid"
    ACTIVE = "active"
    EXPIRED = "expired"
    GRACE = "grace"
    REVOKED = "revoked"
    SERVER_UNREACHABLE = "server_unreachable"


class LicenseEdition(str, Enum):
    STARTER = "starter"
    PROFESSIONAL = "professional"
    BUSINESS = "business"


@dataclass
class LicenseDocument:
    license_id: str
    customer_reference: str
    instance_id: str
    edition: LicenseEdition
    allowed_features: list[str]
    max_staff: int  # -1 = unlimited
    max_services: int  # -1 = unlimited
    max_bookings_per_month: int | None
    issued_at: datetime
    expires_at: datetime | None
    last_validated_at: datetime | None
    grace_until: datetime | None
    signature: str


@dataclass
class LicenseState:
    status: LicenseStatus
    document: LicenseDocument | None = None
    message: str = ""
    # Demo mode counters (populated from DB at startup)
    demo_booking_count: int = 0
    demo_staff_count: int = 0
    demo_service_count: int = 0
    demo_started_at: datetime | None = None

    # Hard limits for Demo/Eval mode
    DEMO_MAX_BOOKINGS: int = field(default=5, init=False, repr=False)
    DEMO_MAX_STAFF: int = field(default=2, init=False, repr=False)
    DEMO_MAX_SERVICES: int = field(default=3, init=False, repr=False)
    DEMO_MAX_DAYS: int = field(default=30, init=False, repr=False)

    def __post_init__(self) -> None:
        self.DEMO_MAX_BOOKINGS = 5
        self.DEMO_MAX_STAFF = 2
        self.DEMO_MAX_SERVICES = 3
        self.DEMO_MAX_DAYS = 30

    @property
    def demo_limits_reached(self) -> bool:
        if self.demo_booking_count >= self.DEMO_MAX_BOOKINGS:
            return True
        if self.demo_staff_count >= self.DEMO_MAX_STAFF:
            return True
        if self.demo_service_count >= self.DEMO_MAX_SERVICES:
            return True
        if self.demo_started_at is not None:
            age = (datetime.now(timezone.utc) - self.demo_started_at).days
            if age >= self.DEMO_MAX_DAYS:
                return True
        return False

    @property
    def bookings_allowed(self) -> bool:
        """Whether new bookings may be created."""
        if self.status == LicenseStatus.ACTIVE:
            return True
        if self.status in (LicenseStatus.GRACE, LicenseStatus.SERVER_UNREACHABLE):
            return True
        if self.status == LicenseStatus.MISSING:
            return not self.demo_limits_reached
        if self.status == LicenseStatus.EXPIRED:
            # allowed only while grace period is still active
            if self.document and self.document.grace_until:
                return datetime.now(timezone.utc) < self.document.grace_until
        return False

    def is_feature_allowed(self, feature: str) -> bool:
        if self.document is None:
            return False
        return feature in self.document.allowed_features

    def check_staff_limit(self, current_count: int) -> bool:
        if self.status == LicenseStatus.MISSING:
            return current_count < self.DEMO_MAX_STAFF
        if self.document is None:
            return False
        if self.document.max_staff == -1:
            return True
        return current_count < self.document.max_staff

    def check_service_limit(self, current_count: int) -> bool:
        if self.status == LicenseStatus.MISSING:
            return current_count < self.DEMO_MAX_SERVICES
        if self.document is None:
            return False
        if self.document.max_services == -1:
            return True
        return current_count < self.document.max_services


# ---------------------------------------------------------------------------
# Module-level singleton (populated at application startup)
# ---------------------------------------------------------------------------
_current_state: LicenseState = LicenseState(
    status=LicenseStatus.MISSING,
    message="License not yet evaluated.",
)


def get_license_state() -> LicenseState:
    return _current_state


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _verify_signature(payload_bytes: bytes, signature_b64: str) -> bool:
    try:
        public_key_bytes = base64.b64decode(_PUBLIC_KEY_B64)
        verify_key = nacl.signing.VerifyKey(public_key_bytes)
        signature_bytes = base64.b64decode(signature_b64)
        verify_key.verify(payload_bytes, signature_bytes)
        return True
    except (nacl.exceptions.BadSignatureError, Exception):
        return False


def _canonical_payload(doc: dict[str, Any]) -> bytes:
    """Canonical JSON: keys sorted, no whitespace, signature field excluded."""
    payload = {k: v for k, v in doc.items() if k != "signature"}
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()


def _parse_document(raw: dict[str, Any]) -> LicenseDocument:
    return LicenseDocument(
        license_id=raw["license_id"],
        customer_reference=raw.get("customer_reference", ""),
        instance_id=raw.get("instance_id", ""),
        edition=LicenseEdition(raw["edition"]),
        allowed_features=raw.get("allowed_features", []),
        max_staff=raw.get("max_staff", -1),
        max_services=raw.get("max_services", -1),
        max_bookings_per_month=raw.get("max_bookings_per_month"),
        issued_at=_parse_dt(raw["issued_at"]) or _now(),
        expires_at=_parse_dt(raw.get("expires_at")),
        last_validated_at=_parse_dt(raw.get("last_validated_at")),
        grace_until=_parse_dt(raw.get("grace_until")),
        signature=raw["signature"],
    )


# ---------------------------------------------------------------------------
# Core validation logic
# ---------------------------------------------------------------------------

def _evaluate_document(doc: LicenseDocument, grace_days: int) -> LicenseState:
    now = _now()

    # Step 1: Check for explicit revocation in the document field
    # (broker may embed status = revoked when issuing/updating the document)

    # Step 2: Expiry check
    if doc.expires_at and now > doc.expires_at:
        grace_until = doc.grace_until
        if grace_until and now < grace_until:
            return LicenseState(
                status=LicenseStatus.GRACE,
                document=doc,
                message="License has expired but is within the grace period.",
            )
        return LicenseState(
            status=LicenseStatus.EXPIRED,
            document=doc,
            message="License has expired and the grace period has elapsed.",
        )

    # Step 3: Grace window from last_validated_at
    if doc.last_validated_at:
        from datetime import timedelta
        deadline = doc.last_validated_at + timedelta(days=grace_days)
        if now > deadline:
            return LicenseState(
                status=LicenseStatus.EXPIRED,
                document=doc,
                message="Online validation overdue and grace period elapsed.",
            )

    return LicenseState(
        status=LicenseStatus.ACTIVE,
        document=doc,
        message="License is valid.",
    )


def validate_license_from_env(
    license_key: str,
    grace_days: int = 30,
) -> LicenseState:
    """
    Validate a base64-encoded license document string.
    Returns a LicenseState without modifying the module-level singleton.
    """
    if not license_key.strip():
        return LicenseState(
            status=LicenseStatus.MISSING,
            message="No license key configured. Running in Demo/Eval mode.",
        )

    # Decode JSON
    try:
        raw_json = base64.b64decode(license_key.strip()).decode()
        raw: dict[str, Any] = json.loads(raw_json)
    except Exception:
        return LicenseState(
            status=LicenseStatus.INVALID,
            message="License key could not be decoded. The key may be malformed.",
        )

    # Verify signature
    if not _verify_signature(_canonical_payload(raw), raw.get("signature", "")):
        return LicenseState(
            status=LicenseStatus.INVALID,
            message="License signature verification failed. The license may have been tampered with.",
        )

    # Parse document
    try:
        doc = _parse_document(raw)
    except (KeyError, ValueError) as exc:
        return LicenseState(
            status=LicenseStatus.INVALID,
            message=f"License document is structurally invalid: {exc}",
        )

    return _evaluate_document(doc, grace_days)


def load_license_from_file(path: Path, grace_days: int = 30) -> LicenseState:
    """Load and validate a license from a JSON file."""
    try:
        raw: dict[str, Any] = json.loads(path.read_text())
    except Exception:
        return LicenseState(
            status=LicenseStatus.INVALID,
            message=f"Could not read license file at {path}.",
        )

    if not _verify_signature(_canonical_payload(raw), raw.get("signature", "")):
        return LicenseState(
            status=LicenseStatus.INVALID,
            message="License file signature verification failed.",
        )

    try:
        doc = _parse_document(raw)
    except (KeyError, ValueError) as exc:
        return LicenseState(
            status=LicenseStatus.INVALID,
            message=f"License file is structurally invalid: {exc}",
        )

    return _evaluate_document(doc, grace_days)


def initialize_license(
    license_key: str,
    grace_days: int = 30,
    data_dir: Path | None = None,
) -> LicenseState:
    """
    Called once at application startup. Sets the module-level singleton.
    Reads from env var first, then falls back to /data/license.json.
    """
    global _current_state

    state: LicenseState

    if license_key.strip():
        state = validate_license_from_env(license_key, grace_days)
    elif data_dir and (data_dir / "license.json").exists():
        state = load_license_from_file(data_dir / "license.json", grace_days)
    else:
        state = LicenseState(
            status=LicenseStatus.MISSING,
            message="No license key configured. Running in Demo/Eval mode.",
        )

    _current_state = state
    return state


def get_or_create_instance_id(
    configured_id: str,
    data_dir: Path,
) -> str:
    """
    Return the instance ID from env var, persisted file, or generate a new one.
    """
    if configured_id.strip():
        return configured_id.strip()

    id_file = data_dir / "instance_id"
    if id_file.exists():
        return id_file.read_text().strip()

    new_id = str(uuid.uuid4())
    try:
        data_dir.mkdir(parents=True, exist_ok=True)
        id_file.write_text(new_id)
    except OSError:
        pass  # non-fatal: instance_id won't persist across restarts
    return new_id
