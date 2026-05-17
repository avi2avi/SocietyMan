from email.message import EmailMessage
import smtplib
from typing import Optional

from app.core.config import settings


def _send_email(to_email: str, subject: str, body: str) -> bool:
    if not settings.smtp_host or not settings.smtp_from:
        print(f"EMAIL -> {to_email}: {subject}\n{body}")
        return False

    msg = EmailMessage()
    msg["From"] = settings.smtp_from
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        if settings.smtp_use_tls and settings.smtp_port in (465, 587):
            # Try SSL first for 465, TLS for 587
            if settings.smtp_port == 465:
                with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port) as server:
                    if settings.smtp_username and settings.smtp_password:
                        server.login(settings.smtp_username, settings.smtp_password)
                    server.send_message(msg)
            else:
                with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                    server.starttls()
                    if settings.smtp_username and settings.smtp_password:
                        server.login(settings.smtp_username, settings.smtp_password)
                    server.send_message(msg)
            return True
        else:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                if settings.smtp_username and settings.smtp_password:
                    server.login(settings.smtp_username, settings.smtp_password)
                server.send_message(msg)
            return True
    except Exception as exc:
        print(f"Failed to send email to {to_email}: {exc}")
        return False


def notify_visitor_arrival(resident_user_id: int, visitor_name: str) -> None:
    # Placeholder for app push + WhatsApp integration; also log for now
    print(f"Notify resident {resident_user_id}: visitor {visitor_name} arrived")
    # In future, look up resident email and send a notification via _send_email or WhatsApp


def notify_ticket_update(resident_user_id: int, ticket_id: int, status: str) -> None:
    print(f"Notify resident {resident_user_id}: ticket {ticket_id} updated to {status}")


def send_payment_reminder(resident_user_id: int, amount: float) -> None:
    print(f"Reminder to resident {resident_user_id}: pending amount {amount}")


def send_admin_verification_code(email: str | None, phone: str | None, code: str) -> None:
    subject = "Your admin verification code"
    body = f"Your verification code is: {code}\n\nThis code expires in 10 minutes."
    sent = False
    if email:
        sent = _send_email(email, subject, body)
    else:
        print(f"ADMIN VERIFICATION CODE FOR {phone}: {code}")

    # For local testing or SMTP failures, persist the code so admins are not locked out.
    try:
        if not sent:
            from pathlib import Path

            p = Path("scripts/last_admin_code.txt")
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(f"{email or phone}:{code}")
    except Exception:
        pass


def send_society_admin_credentials(email: str | None, phone: str | None, username: str, password: str) -> None:
    subject = "Your SocietyMan admin credentials"
    body = (
        f"Your society admin account has been created or activated.\n"
        f"Username: {username}\n"
        f"Password: {password}\n"
        f"Please change your password after first login."
    )
    if email:
        _send_email(email, subject, body)
    print(f"SOCIETY ADMIN CREDENTIALS -> {email or phone}: {body}")
    try:
        if not settings.smtp_host or not settings.smtp_from:
            from pathlib import Path

            p = Path("scripts/society_admin_credentials.txt")
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(f"{email or phone}:{username}:{password}\n")
    except Exception:
        pass
