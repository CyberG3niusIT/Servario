"""Erstellt Notification-Datensätze und versendet E-Mails."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import Booking
from app.models.notification import Notification, NotificationChannel, NotificationStatus, NotificationType
from app.models.settings import InstanceSettings
from app.services import email as email_svc

logger = logging.getLogger(__name__)

_DEFAULT_BUSINESS = "Servario"
_DEFAULT_FROM = "noreply@example.com"

SmtpConfig = tuple[str, int, str, str]


async def _get_instance_settings(db: AsyncSession) -> InstanceSettings | None:
    return await db.get(InstanceSettings, 1)


async def _resolve_context(db: AsyncSession) -> tuple[str, str, SmtpConfig | None]:
    """Gibt (business_name, from_email, smtp_override|None) zurück."""
    row = await _get_instance_settings(db)
    if row:
        name = row.business_name or _DEFAULT_BUSINESS
        mail = row.business_email or _DEFAULT_FROM
        smtp: SmtpConfig | None = None
        if row.smtp_host and row.smtp_user and row.smtp_password_encrypted:
            smtp = (row.smtp_host, row.smtp_port or 587, row.smtp_user, row.smtp_password_encrypted)
        return name, mail, smtp
    return _DEFAULT_BUSINESS, _DEFAULT_FROM, None


async def _create_notification_record(
    db: AsyncSession,
    *,
    booking: Booking,
    notification_type: NotificationType,
    recipient_email: str,
) -> Notification:
    n = Notification(
        booking_id=booking.id,
        notification_type=notification_type,
        channel=NotificationChannel.EMAIL,
        recipient_email=recipient_email,
        status=NotificationStatus.PENDING,
    )
    db.add(n)
    await db.flush()
    return n


async def _mark(db: AsyncSession, n: Notification, *, success: bool, error: str | None = None) -> None:
    n.status = NotificationStatus.SENT if success else NotificationStatus.FAILED
    n.sent_at = datetime.now(tz=timezone.utc) if success else None
    n.error_message = error
    await db.flush()


async def send_confirmation(db: AsyncSession, booking: Booking) -> None:
    customer = booking.customer
    if not customer or not customer.email:
        logger.info("Keine Kunden-E-Mail für Buchung %s – Bestätigung übersprungen", booking.id)
        return

    business_name, from_email, smtp_override = await _resolve_context(db)
    n = await _create_notification_record(
        db, booking=booking, notification_type=NotificationType.CONFIRMATION,
        recipient_email=customer.email,
    )

    try:
        await email_svc.send_booking_confirmation(
            to_email=customer.email,
            customer_name=customer.name or customer.email,
            service_name=booking.service.name,
            team_member_name=booking.team_member.display_name or "",
            start_at=booking.start_at,
            end_at=booking.end_at,
            duration_minutes=booking.service.duration_minutes,
            price=str(booking.service.price) if booking.service.price else None,
            customer_notes=booking.customer_notes,
            business_name=business_name,
            from_email=from_email,
            smtp_override=smtp_override,
        )
        await _mark(db, n, success=True)
    except Exception as exc:
        await _mark(db, n, success=False, error=str(exc))


async def send_cancellation(db: AsyncSession, booking: Booking) -> None:
    customer = booking.customer
    if not customer or not customer.email:
        return

    business_name, from_email, smtp_override = await _resolve_context(db)
    n = await _create_notification_record(
        db, booking=booking, notification_type=NotificationType.CANCELLATION,
        recipient_email=customer.email,
    )

    try:
        await email_svc.send_booking_cancellation(
            to_email=customer.email,
            customer_name=customer.name or customer.email,
            service_name=booking.service.name,
            team_member_name=booking.team_member.display_name or "",
            start_at=booking.start_at,
            end_at=booking.end_at,
            business_name=business_name,
            from_email=from_email,
            smtp_override=smtp_override,
        )
        await _mark(db, n, success=True)
    except Exception as exc:
        await _mark(db, n, success=False, error=str(exc))


async def send_reminder(db: AsyncSession, booking: Booking) -> None:
    customer = booking.customer
    if not customer or not customer.email:
        return

    business_name, from_email, smtp_override = await _resolve_context(db)
    n = await _create_notification_record(
        db, booking=booking, notification_type=NotificationType.REMINDER,
        recipient_email=customer.email,
    )

    try:
        await email_svc.send_booking_reminder(
            to_email=customer.email,
            customer_name=customer.name or customer.email,
            service_name=booking.service.name,
            team_member_name=booking.team_member.display_name or "",
            start_at=booking.start_at,
            end_at=booking.end_at,
            duration_minutes=booking.service.duration_minutes,
            business_name=business_name,
            from_email=from_email,
            smtp_override=smtp_override,
        )
        await _mark(db, n, success=True)
    except Exception as exc:
        await _mark(db, n, success=False, error=str(exc))
