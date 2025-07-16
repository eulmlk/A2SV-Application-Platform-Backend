# seed.py

from app.core.database import SessionLocal
from app.models.role import Role  # Assuming your Role model is in app/models/role.py


def seed_roles():
    """Seeds the database with initial roles."""
    db = SessionLocal()

    # --- DEFINE YOUR REQUIRED ROLES HERE ---
    initial_roles = ["applicant", "reviewer", "admin"]

    print("Seeding initial roles...")

    try:
        for role_name in initial_roles:
            # Check if role already exists
            role_exists = db.query(Role).filter(Role.name == role_name).first()
            if not role_exists:
                # Create and add the new role
                new_role = Role(name=role_name)
                db.add(new_role)
                print(f"  - Created role: '{role_name}'")
            else:
                print(f"  - Role '{role_name}' already exists. Skipping.")

        # Commit all the changes at once
        db.commit()
        print("✅ Seeding complete.")

    except Exception as e:
        print(f"❌ An error occurred during seeding: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_roles()
