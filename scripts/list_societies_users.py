#!/usr/bin/env python
"""List societies and associated users; test common test passwords against stored hashes."""
import sys
sys.path.insert(0, '.')

from app.core.database import SessionLocal
from app.models.entities import Society, User
from app.core.security import verify_password
from app.core.config import settings

candidates = [settings.default_admin_password, "admin123", "gate123", "resident123"]

with SessionLocal() as db:
    societies = db.query(Society).order_by(Society.name).all()
    if not societies:
        print("No societies found in database.")
    for s in societies:
        print(f"\nSociety: {s.name} (id={s.id})")
        print(f"  admin_contact: {s.admin_contact_name} <{s.admin_contact_email}> phone={s.admin_contact_phone} approved={s.is_approved}")
        users = db.query(User).filter(User.society_id == s.id).order_by(User.role).all()
        if not users:
            print("  No users registered for this society.")
            continue
        for u in users:
            matched = None
            for p in candidates:
                try:
                    if verify_password(p, u.password_hash):
                        matched = p
                        break
                except Exception:
                    pass
            print(f"  - {u.role}: {u.full_name} <{u.email}> phone={u.phone} id={u.id} password_match={matched or 'unknown'}")

    # Also show default admin
    admin = db.query(User).filter(User.email == settings.default_admin_email).first()
    if admin:
        print(f"\nDefault admin: {admin.full_name} <{admin.email}> phone={admin.phone} id={admin.id} role={admin.role}")
        print(f"  Known password: {settings.default_admin_password}")
    else:
        print("\nDefault admin user not found in users table.")
