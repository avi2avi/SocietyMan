from email.message import EmailMessage
import smtplib
import sys

from app.core.config import settings


def main() -> int:
    to_email = sys.argv[1] if len(sys.argv) > 1 else settings.smtp_username
    if not to_email:
        print("Usage: python scripts/test_smtp.py recipient@example.com")
        return 2
    if not settings.smtp_host or not settings.smtp_from:
        print("SMTP_HOST and SMTP_FROM must be configured in .env")
        return 2

    msg = EmailMessage()
    msg["From"] = settings.smtp_from
    msg["To"] = to_email
    msg["Subject"] = "SocietyMan SMTP test"
    msg.set_content("SMTP is configured correctly. Admin verification codes can now be delivered by email.")

    if settings.smtp_port == 465:
        with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port) as server:
            if settings.smtp_username and settings.smtp_password:
                server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(msg)
    else:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            if settings.smtp_use_tls:
                server.starttls()
            if settings.smtp_username and settings.smtp_password:
                server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(msg)

    print(f"SMTP test email sent to {to_email}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
