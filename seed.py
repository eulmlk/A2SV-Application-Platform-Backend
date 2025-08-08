import os
from app.core.database import Base
from app.models.role import Role
from app.models.user import User
from app.core.security import hash_password
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
Base.metadata.create_all(engine)


def add_description_column_to_cycle():
    """Add the 'description' column to the application_cycles table if it does not exist."""
    db = Session(bind=engine)
    try:
        result = db.execute(
            text(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'application_cycles' AND column_name = 'description'
                """
            )
        )
        if not result.fetchone():
            print("Adding 'description' column to application_cycles table...")
            db.execute(
                text(
                    "ALTER TABLE application_cycles ADD COLUMN description VARCHAR(500) NULL"
                )
            )
            db.commit()
            print("Successfully added 'description' column.")
        else:
            print("Column 'description' already exists in application_cycles table.")
    except Exception as e:
        print(f"Error adding 'description' column: {e}")
        db.rollback()
    finally:
        db.close()


def seed_roles_and_admin():
    db = Session(bind=engine)
    try:
        # Seed roles
        roles = [
            {"id": 1, "name": "applicant"},
            {"id": 2, "name": "reviewer"},
            {"id": 3, "name": "manager"},
            {"id": 4, "name": "admin"},
        ]
        print("Seeding roles...")
        for role in roles:
            if not db.query(Role).filter_by(id=role["id"]).first():
                db.add(Role(id=role["id"], name=role["name"]))
        db.commit()
        print("Roles seeded.")

        # Seed admin user from environment variables
        admin_email = os.getenv("ADMIN_EMAIL", "some_admin_email@gmail.com")
        admin_password = os.getenv("ADMIN_PASSWORD", "some_admin_password")
        admin_role_id = 4
        if not db.query(User).filter_by(email=admin_email).first():
            print(f"Creating admin user: {admin_email}...")
            admin_user = User(
                email=admin_email,
                password=hash_password(admin_password),
                full_name="Admin User",
                role_id=admin_role_id,
            )
            db.add(admin_user)
            db.commit()
            print(f"Admin user created with password: {admin_password}")
        else:
            print(f"Admin user already exists: {admin_email}")
    except Exception as e:
        print(f"An error occurred during seeding: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    add_description_column_to_cycle()
    seed_roles_and_admin()
    print("Seeding script finished.")
