from fastapi import APIRouter, Request

from app.core.license import LicenseStatus, get_license_state

router = APIRouter()


@router.get("/license/status")
async def license_status(request: Request) -> dict:
    state = get_license_state()
    doc = state.document
    instance_id = getattr(request.app.state, "instance_id", "unknown")

    return {
        "status": state.status.value,
        "message": state.message,
        "bookings_allowed": state.bookings_allowed,
        "instance_id": instance_id,
        "demo_limits_reached": (
            state.demo_limits_reached
            if state.status == LicenseStatus.MISSING
            else False
        ),
        # Lizenz-Felder (null wenn keine gültige Lizenz vorhanden)
        "edition": doc.edition.value if doc else None,
        "expires_at": doc.expires_at.isoformat() if doc and doc.expires_at else None,
        "grace_until": doc.grace_until.isoformat() if doc and doc.grace_until else None,
        "max_staff": doc.max_staff if doc else None,
        "max_services": doc.max_services if doc else None,
    }
