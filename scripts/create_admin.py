from app.core.database import SessionLocal
from app.models.entities import User
from app.core.enums import Role
from app.core.security import hash_password

with SessionLocal() as db:
    if db.query(User).filter(User.email == 'admin@example.com').first():
        print('admin@example.com already exists')
    else:
        admin = User(
            full_name='Local Admin',
            phone='0000000000',
            email='admin@example.com',
            password_hash=hash_password('Admin@123'),
            role=Role.ADMIN,
            is_active=True,
        )
        db.add(admin)
        db.commit()
        print('created admin@example.com')
