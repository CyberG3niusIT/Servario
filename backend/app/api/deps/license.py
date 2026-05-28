from fastapi import HTTPException, status

from app.core.license import LicenseStatus, get_license_state


def require_booking_allowed() -> None:
    """FastAPI dependency: raises 402 if new bookings are not permitted."""
    state = get_license_state()
    if not state.bookings_allowed:
        if state.status == LicenseStatus.MISSING:
            detail = "Demo mode limit reached. A valid license is required to create new bookings."
        elif state.status == LicenseStatus.INVALID:
            detail = "License is invalid. Please provide a valid license key."
        elif state.status in (LicenseStatus.EXPIRED, LicenseStatus.REVOKED):
            detail = "License has expired or been revoked. Please renew your license."
        else:
            detail = "Bookings are not available. Please check your license status."
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=detail)
