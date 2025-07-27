import os
from app.core.database import Base, get_db
from app.models.role import Role
from app.models.user import User
from app.core.security import hash_password
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
Base.metadata.create_all(engine)

def seed_roles_and_admin():
    db = Session(bind=engine)
    # Seed roles
    roles = [
        {"id": 1, "name": "applicant"},
        {"id": 2, "name": "reviewer"},
        {"id": 3, "name": "manager"},
        {"id": 4, "name": "admin"},
    ]
    for role in roles:
        if not db.query(Role).filter_by(id=role["id"]).first():
            db.add(Role(id=role["id"], name=role["name"]))
    db.commit()

    # Seed admin user from environment variables
    admin_email = os.getenv("ADMIN_EMAIL", "some_admin_email@gmail.com")
    admin_password = os.getenv("ADMIN_PASSWORD", "some_admin_password")
    admin_role_id = 4
    if not db.query(User).filter_by(email=admin_email).first():
        admin_user = User(
            id=None,  # Let default uuid be generated
            email=admin_email,
            password=hash_password(admin_password),
            full_name="Admin User",
            role_id=admin_role_id
        )
        db.add(admin_user)
        db.commit()
        print(f"Admin user created: {admin_email} / {admin_password}")
    else:
        print(f"Admin user already exists: {admin_email}")
    db.close()

if __name__ == "__main__":
    seed_roles_and_admin()
