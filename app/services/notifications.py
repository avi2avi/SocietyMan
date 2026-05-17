def notify_visitor_arrival(resident_user_id: int, visitor_name: str) -> None:
    # Placeholder for app push + WhatsApp integration
    print(f"Notify resident {resident_user_id}: visitor {visitor_name} arrived")


def notify_ticket_update(resident_user_id: int, ticket_id: int, status: str) -> None:
    print(f"Notify resident {resident_user_id}: ticket {ticket_id} updated to {status}")


def send_payment_reminder(resident_user_id: int, amount: float) -> None:
    print(f"Reminder to resident {resident_user_id}: pending amount {amount}")


def send_admin_verification_code(email: str, code: str) -> None:
    print(f"ADMIN VERIFICATION CODE for {email}: {code}")
    print("(In production this code should be sent to the registered email address.)")
