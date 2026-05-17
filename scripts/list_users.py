from app.core.database import SessionLocal
from app.models.entities import User

with SessionLocal() as db:
    users = db.query(User).all()
    for u in users:
        print(u.id, u.email, u.phone, u.role, u.is_active)
