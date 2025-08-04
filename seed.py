import os
from app.core.database import Base, get_db
from app.models.role import Role
from app.models.user import User
from app.core.security import hash_password
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
Base.metadata.create_all(engine)

def rename_degree_to_student_id():
    """Rename the 'degree' column to 'student_id' in the applications table"""
    db = Session(bind=engine)
    try:
        # Check if the degree column exists
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'applications' AND column_name = 'degree'
        """))
        
        if result.fetchone():
            # Rename the column
            db.execute(text("ALTER TABLE applications RENAME COLUMN degree TO student_id"))
            db.commit()
            print("Successfully renamed 'degree' column to 'student_id' in applications table")
        else:
            # Check if student_id column already exists
            result = db.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'applications' AND column_name = 'student_id'
            """))
            
            if result.fetchone():
                print("Column 'student_id' already exists in applications table")
            else:
                print("Column 'degree' not found in applications table")
    except Exception as e:
        print(f"Error renaming column: {e}")
        db.rollback()
    finally:
        db.close()

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
    rename_degree_to_student_id()
    seed_roles_and_admin()
