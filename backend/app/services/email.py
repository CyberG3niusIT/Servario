"""E-Mail-Versand via aiosmtplib mit Jinja2-Templates."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path

import aiosmtplib
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

_jinja = Environment(
    loader=FileSystemLoader(str(_TEMPLATES_DIR)),
    autoescape=select_autoescape(["html"]),
)

SmtpConfig = tuple[str, int, str, str]  # host, port, user, password


def _render(template_name: str, context: dict) -> str:
    return _jinja.get_template(template_name).render(**context)


def _smtp_config(override: SmtpConfig | None = None) -> SmtpConfig | None:
    """Gibt (host, port, user, password) zurück; override schlägt Env-Vars."""
    if override:
        return override
    s = get_settings()
    if s.smtp_host and s.smtp_user:
        return s.smtp_host, s.smtp_port, s.smtp_user, s.smtp_password
    return None


async def send_booking_confirmation(
    *,
    to_email: str,
    customer_name: str,
    service_name: str,
    team_member_name: str,
    start_at: datetime,
    end_at: datetime,
    duration_minutes: int,
    price: str | None,
    customer_notes: str | None,
    business_name: str,
    from_email: str,
    smtp_override: SmtpConfig | None = None,
) -> None:
    context = {
        "business_name": business_name,
        "customer_name": customer_name,
        "service_name": service_name,
        "team_member_name": team_member_name,
        "start_date": start_at.strftime("%d.%m.%Y"),
        "start_time": start_at.strftime("%H:%M"),
        "end_time": end_at.strftime("%H:%M"),
        "duration_minutes": duration_minutes,
        "price": price,
        "customer_notes": customer_notes,
    }
    html = _render("email/booking_confirmation.html", context)
    subject = f"Buchungsbestätigung – {service_name} am {context['start_date']}"
    await _send(to=to_email, subject=subject, html=html, from_email=from_email, smtp_override=smtp_override)


async def send_booking_cancellation(
    *,
    to_email: str,
    customer_name: str,
    service_name: str,
    team_member_name: str,
    start_at: datetime,
    end_at: datetime,
    business_name: str,
    from_email: str,
    smtp_override: SmtpConfig | None = None,
) -> None:
    context = {
        "business_name": business_name,
        "customer_name": customer_name,
        "service_name": service_name,
        "team_member_name": team_member_name,
        "start_date": start_at.strftime("%d.%m.%Y"),
        "start_time": start_at.strftime("%H:%M"),
        "end_time": end_at.strftime("%H:%M"),
    }
    html = _render("email/booking_cancellation.html", context)
    subject = f"Terminabsage – {service_name} am {context['start_date']}"
    await _send(to=to_email, subject=subject, html=html, from_email=from_email, smtp_override=smtp_override)


async def send_booking_reminder(
    *,
    to_email: str,
    customer_name: str,
    service_name: str,
    team_member_name: str,
    start_at: datetime,
    end_at: datetime,
    duration_minutes: int,
    business_name: str,
    from_email: str,
    smtp_override: SmtpConfig | None = None,
) -> None:
    context = {
        "business_name": business_name,
        "customer_name": customer_name,
        "service_name": service_name,
        "team_member_name": team_member_name,
        "start_date": start_at.strftime("%d.%m.%Y"),
        "start_time": start_at.strftime("%H:%M"),
        "end_time": end_at.strftime("%H:%M"),
        "duration_minutes": duration_minutes,
    }
    html = _render("email/booking_reminder.html", context)
    subject = f"Terminerinnerung – {service_name} am {context['start_date']}"
    await _send(to=to_email, subject=subject, html=html, from_email=from_email, smtp_override=smtp_override)


async def _send(
    *,
    to: str,
    subject: str,
    html: str,
    from_email: str,
    smtp_override: SmtpConfig | None = None,
) -> None:
    cfg = _smtp_config(smtp_override)
    if not cfg:
        logger.warning("SMTP nicht konfiguriert – E-Mail an %s nicht versendet: %s", to, subject)
        return

    host, port, user, password = cfg
    msg = EmailMessage()
    msg["From"] = from_email
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content("Bitte aktivieren Sie HTML-E-Mails, um diese Nachricht anzuzeigen.")
    msg.add_alternative(html, subtype="html")

    try:
        await aiosmtplib.send(
            msg,
            hostname=host,
            port=port,
            username=user,
            password=password,
            start_tls=True,
        )
        logger.info("E-Mail gesendet an %s: %s", to, subject)
    except Exception as exc:
        logger.error("E-Mail-Versand fehlgeschlagen an %s: %s – %s", to, subject, exc)
        raise
