import os
from app.core.database import Base
from app.models.role import Role
from app.models.user import User
from app.core.security import hash_password
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from app.core.config import settings
from app.models.application import Application
from app.models.review import Review
from app.models.application_cycle import ApplicationCycle

engine = create_engine(settings.DATABASE_URL)
Base.metadata.create_all(engine)


def add_profile_picture_column():
    """Add the 'profile_picture_url' column to the users table if it does not exist."""
    db = Session(bind=engine)
    try:
        result = db.execute(
            text(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'profile_picture_url'
                """
            )
        )
        if not result.fetchone():
            print("Adding 'profile_picture_url' column to users table...")
            db.execute(
                text("ALTER TABLE users ADD COLUMN profile_picture_url VARCHAR(512) NULL")
            )
            db.commit()
            print("Successfully added 'profile_picture_url' column.")
        else:
            print("Column 'profile_picture_url' already exists in users table.")
    except Exception as e:
        print(f"Error adding 'profile_picture_url' column: {e}")
        db.rollback()
    finally:
        db.close()


def add_country_column():
    """Ensure 'country' column exists, is populated, and is NOT NULL."""
    db = Session(bind=engine)
    try:
        # Check if the column exists
        result = db.execute(
            text(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'applications' AND column_name = 'country'
                """
            )
        )
        if not result.fetchone():
            print("Column 'country' not found. Creating, populating, and setting NOT NULL...")
            # Atomically add the column, populate existing rows, and set NOT NULL
            db.execute(
                text("ALTER TABLE applications ADD COLUMN country VARCHAR(255) NOT NULL DEFAULT 'Ethiopia'")
            )
            # Remove the default so it doesn't apply to new records
            db.execute(
                text("ALTER TABLE applications ALTER COLUMN country DROP DEFAULT")
            )
            print("Successfully created 'country' column and populated existing rows.")
        else:
            print("Column 'country' exists. Checking for and populating NULL values...")
            # If the column exists, it might have NULLs. Update them.
            db.execute(
                text("UPDATE applications SET country = 'Ethiopia' WHERE country IS NULL")
            )
            # Ensure the NOT NULL constraint is in place for future inserts
            db.execute(
                text("ALTER TABLE applications ALTER COLUMN country SET NOT NULL")
            )
            print("Ensured all existing rows in 'country' column are populated and column is NOT NULL.")

        db.commit()
    except Exception as e:
        print(f"Error modifying 'country' column: {e}")
        db.rollback()
    finally:
        db.close()


def add_degree_column():
    """Ensure 'degree' column exists, is populated, and is NOT NULL."""
    db = Session(bind=engine)
    try:
        # Check if the column exists
        result = db.execute(
            text(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'applications' AND column_name = 'degree'
                """
            )
        )
        if not result.fetchone():
            print("Column 'degree' not found. Creating, populating, and setting NOT NULL...")
            # Atomically add the column, populate existing rows, and set NOT NULL
            db.execute(
                text("ALTER TABLE applications ADD COLUMN degree VARCHAR(255) NOT NULL DEFAULT 'B.Sc. in Software Engineering'")
            )
            # Remove the default so it doesn't apply to new records
            db.execute(
                text("ALTER TABLE applications ALTER COLUMN degree DROP DEFAULT")
            )
            print("Successfully created 'degree' column and populated existing rows.")
        else:
            print("Column 'degree' exists. Checking for and populating NULL values...")
            # If the column exists, it might have NULLs. Update them.
            db.execute(
                text("UPDATE applications SET degree = 'B.Sc. in Software Engineering' WHERE degree IS NULL")
            )
            # Ensure the NOT NULL constraint is in place for future inserts
            db.execute(
                text("ALTER TABLE applications ALTER COLUMN degree SET NOT NULL")
            )
            print("Ensured all existing rows in 'degree' column are populated and column is NOT NULL.")

        db.commit()
    except Exception as e:
        print(f"Error modifying 'degree' column: {e}")
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
    add_profile_picture_column()
    add_country_column()
    add_degree_column()
    seed_roles_and_admin()
    print("Seeding script finished.")