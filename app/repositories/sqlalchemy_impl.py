from sqlalchemy.orm import Session
from app.domain.entities import User, Application
from app.models.user import User as UserModel
from app.models.application import Application as ApplicationModel
from app.repositories.interfaces import IUserRepository, IApplicationRepository
import uuid
from app.models.role import Role as RoleModel
from app.models.application_cycle import ApplicationCycle as ApplicationCycleModel
from app.domain.entities import Role, ApplicationCycle
from app.repositories.interfaces import IRoleRepository, IApplicationCycleRepository

class UserRepository(IUserRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str):
        user = self.db.query(UserModel).filter(UserModel.email == email).first()
        if user:
            return User(
                id=user.id,
                email=user.email,
                password=user.password,
                full_name=user.full_name,
                role_id=user.role_id,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
        return None

    def get_by_id(self, user_id: uuid.UUID):
        user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if user:
            return User(
                id=user.id,
                email=user.email,
                password=user.password,
                full_name=user.full_name,
                role_id=user.role_id,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
        return None

    def create(self, user: User):
        db_user = UserModel(
            id=user.id,
            email=user.email,
            password=user.password,
            full_name=user.full_name,
            role_id=user.role_id
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return User(
            id=db_user.id,
            email=db_user.email,
            password=db_user.password,
            full_name=db_user.full_name,
            role_id=db_user.role_id,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at
        )

    def list_all(self):
        users = self.db.query(UserModel).all()
        return [User(
            id=u.id,
            email=u.email,
            password=u.password,
            full_name=u.full_name,
            role_id=u.role_id,
            created_at=u.created_at,
            updated_at=u.updated_at
        ) for u in users]

    def update(self, user_id: uuid.UUID, **kwargs):
        user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            return None
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        self.db.commit()
        self.db.refresh(user)
        return User(
            id=user.id,
            email=user.email,
            password=user.password,
            full_name=user.full_name,
            role_id=user.role_id,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

    def delete(self, user_id: uuid.UUID):
        user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            return False
        self.db.delete(user)
        self.db.commit()
        return True

class ApplicationRepository(IApplicationRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, application_id: uuid.UUID):
        app = self.db.query(ApplicationModel).filter(ApplicationModel.id == application_id).first()
        if app:
            return Application(
                id=app.id,
                applicant_id=app.applicant_id,
                cycle_id=app.cycle_id,
                status=app.status,
                school=app.school,
                degree=app.degree,
                leetcode_handle=app.leetcode_handle,
                codeforces_handle=app.codeforces_handle,
                essay_why_a2sv=app.essay_why_a2sv,
                essay_about_you=app.essay_about_you,
                resume_url=app.resume_url,
                assigned_reviewer_id=app.assigned_reviewer_id,
                decision_notes=app.decision_notes,
                submitted_at=app.submitted_at,
                updated_at=app.updated_at
            )
        return None

    def get_by_applicant_id(self, applicant_id: uuid.UUID):
        app = self.db.query(ApplicationModel).filter(ApplicationModel.applicant_id == applicant_id).first()
        if app:
            return Application(
                id=app.id,
                applicant_id=app.applicant_id,
                cycle_id=app.cycle_id,
                status=app.status,
                school=app.school,
                degree=app.degree,
                leetcode_handle=app.leetcode_handle,
                codeforces_handle=app.codeforces_handle,
                essay_why_a2sv=app.essay_why_a2sv,
                essay_about_you=app.essay_about_you,
                resume_url=app.resume_url,
                assigned_reviewer_id=app.assigned_reviewer_id,
                decision_notes=app.decision_notes,
                submitted_at=app.submitted_at,
                updated_at=app.updated_at
            )
        return None

    def create(self, application: Application):
        db_app = ApplicationModel(
            id=application.id,
            applicant_id=application.applicant_id,
            cycle_id=application.cycle_id,
            status=application.status,
            school=application.school,
            degree=application.degree,
            leetcode_handle=application.leetcode_handle,
            codeforces_handle=application.codeforces_handle,
            essay_why_a2sv=application.essay_why_a2sv,
            essay_about_you=application.essay_about_you,
            resume_url=application.resume_url,
            assigned_reviewer_id=application.assigned_reviewer_id,
            decision_notes=application.decision_notes
        )
        self.db.add(db_app)
        self.db.commit()
        self.db.refresh(db_app)
        return Application(
            id=db_app.id,
            applicant_id=db_app.applicant_id,
            cycle_id=db_app.cycle_id,
            status=db_app.status,
            school=db_app.school,
            degree=db_app.degree,
            leetcode_handle=db_app.leetcode_handle,
            codeforces_handle=db_app.codeforces_handle,
            essay_why_a2sv=db_app.essay_why_a2sv,
            essay_about_you=db_app.essay_about_you,
            resume_url=db_app.resume_url,
            assigned_reviewer_id=db_app.assigned_reviewer_id,
            decision_notes=db_app.decision_notes,
            submitted_at=db_app.submitted_at,
            updated_at=db_app.updated_at
        )

    def update(self, application: Application):
        db_app = self.db.query(ApplicationModel).filter(ApplicationModel.id == application.id).first()
        if not db_app:
            return None
        for key, value in application.__dict__.items():
            if hasattr(db_app, key) and value is not None:
                setattr(db_app, key, value)

        self.db.commit()
        self.db.refresh(db_app)
        return Application(
            id=db_app.id,
            applicant_id=db_app.applicant_id,
            cycle_id=db_app.cycle_id,
            status=db_app.status,
            school=db_app.school,
            degree=db_app.degree,
            leetcode_handle=db_app.leetcode_handle,
            codeforces_handle=db_app.codeforces_handle,
            essay_why_a2sv=db_app.essay_why_a2sv,
            essay_about_you=db_app.essay_about_you,
            resume_url=db_app.resume_url,
            assigned_reviewer_id=db_app.assigned_reviewer_id,
            decision_notes=db_app.decision_notes,
            submitted_at=db_app.submitted_at,
            updated_at=db_app.updated_at
        )

    def delete(self, application_id: uuid.UUID):
        app = self.db.query(ApplicationModel).filter(ApplicationModel.id == application_id).first()
        if not app:
            return False
        self.db.delete(app)
        self.db.commit()
        return True

    def list_by_reviewer(self, reviewer_id: uuid.UUID):
        apps = self.db.query(ApplicationModel).filter(ApplicationModel.assigned_reviewer_id == reviewer_id).all()
        return [Application(
            id=a.id,
            applicant_id=a.applicant_id,
            cycle_id=a.cycle_id,
            status=a.status,
            school=a.school,
            degree=a.degree,
            leetcode_handle=a.leetcode_handle,
            codeforces_handle=a.codeforces_handle,
            essay_why_a2sv=a.essay_why_a2sv,
            essay_about_you=a.essay_about_you,
            resume_url=a.resume_url,
            assigned_reviewer_id=a.assigned_reviewer_id,
            decision_notes=a.decision_notes,
            submitted_at=a.submitted_at,
            updated_at=a.updated_at
        ) for a in apps]

    def list_by_status(self, status: str):
        return []  # Not needed for applicant workflow

    def assign_reviewer(self, application_id: uuid.UUID, reviewer_id: uuid.UUID):
        return None  # Not needed for applicant workflow

    def finalize_decision(self, application_id: uuid.UUID, status: str, decision_notes: str):
        return None  # Not needed for applicant workflow

    def list_all(self):
        return []  # Not needed for applicant workflow 

class RoleRepository(IRoleRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_name(self, name: str):
        role = self.db.query(RoleModel).filter(RoleModel.name == name).first()
        if role:
            return Role(id=role.id, name=role.name)
        return None

    def get_by_id(self, role_id: int):
        role = self.db.query(RoleModel).filter(RoleModel.id == role_id).first()
        if role:
            return Role(id=role.id, name=role.name)
        return None

    def list_all(self):
        roles = self.db.query(RoleModel).all()
        return [Role(id=r.id, name=r.name) for r in roles]

class ApplicationCycleRepository(IApplicationCycleRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_active(self):
        cycle = self.db.query(ApplicationCycleModel).filter(ApplicationCycleModel.is_active == True).first()
        if cycle:
            return ApplicationCycle(
                id=cycle.id,
                name=cycle.name,
                start_date=cycle.start_date,
                end_date=cycle.end_date,
                is_active=cycle.is_active,
                created_at=cycle.created_at
            )
        return None

    def get_by_id(self, cycle_id: int):
        cycle = self.db.query(ApplicationCycleModel).filter(ApplicationCycleModel.id == cycle_id).first()
        if cycle:
            return ApplicationCycle(
                id=cycle.id,
                name=cycle.name,
                start_date=cycle.start_date,
                end_date=cycle.end_date,
                is_active=cycle.is_active,
                created_at=cycle.created_at
            )
        return None
    
    def get_by_name(self, name: str):
        cycle = self.db.query(ApplicationCycleModel).filter(ApplicationCycleModel.name == name).first()
        if cycle:
            return ApplicationCycle(
                id=cycle.id,
                name=cycle.name,
                start_date=cycle.start_date,
                end_date=cycle.end_date,
                is_active=cycle.is_active,
                created_at=cycle.created_at
            )
        return None

    def create(self, cycle: ApplicationCycle):
        db_cycle = ApplicationCycleModel(
            name=cycle.name,
            start_date=cycle.start_date,
            end_date=cycle.end_date,
            is_active=cycle.is_active
        )
        self.db.add(db_cycle)
        self.db.commit()
        self.db.refresh(db_cycle)
        return ApplicationCycle(
            id=db_cycle.id,
            name=db_cycle.name,
            start_date=db_cycle.start_date,
            end_date=db_cycle.end_date,
            is_active=db_cycle.is_active,
            created_at=db_cycle.created_at
        )

    def activate(self, cycle_id: int):
        # Deactivate all
        self.db.query(ApplicationCycleModel).update({ApplicationCycleModel.is_active: False})
        # Activate one
        cycle = self.db.query(ApplicationCycleModel).filter(ApplicationCycleModel.id == cycle_id).first()
        if not cycle:
            return None
        cycle.is_active = True
        self.db.commit()
        self.db.refresh(cycle)
        return ApplicationCycle(
            id=cycle.id,
            name=cycle.name,
            start_date=cycle.start_date,
            end_date=cycle.end_date,
            is_active=cycle.is_active,
            created_at=cycle.created_at
        )

    def list_all(self):
        cycles = self.db.query(ApplicationCycleModel).all()
        return [ApplicationCycle(
            id=c.id,
            name=c.name,
            start_date=c.start_date,
            end_date=c.end_date,
            is_active=c.is_active,
            created_at=c.created_at
        ) for c in cycles] 

    def update(self, cycle_id: int, **kwargs):
        cycle = self.db.query(ApplicationCycleModel).filter(ApplicationCycleModel.id == cycle_id).first()
        if not cycle:
            return None
        for key, value in kwargs.items():
            if hasattr(cycle, key) and value is not None:
                setattr(cycle, key, value)
        self.db.commit()
        self.db.refresh(cycle)
        return ApplicationCycle(
            id=cycle.id,
            name=cycle.name,
            start_date=cycle.start_date,
            end_date=cycle.end_date,
            is_active=cycle.is_active,
            created_at=cycle.created_at
        )

    def delete(self, cycle_id: int):
        cycle = self.db.query(ApplicationCycleModel).filter(ApplicationCycleModel.id == cycle_id).first()
        if not cycle:
            return False
        self.db.delete(cycle)
        self.db.commit()
        return True 

class ReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_application_id(self, application_id: uuid.UUID):
        from app.models.review import Review as ReviewModel
        review = self.db.query(ReviewModel).filter(ReviewModel.application_id == application_id).first()
        return review

    def create_or_update(self, application_id: uuid.UUID, reviewer_id: uuid.UUID, data: dict):
        from app.models.review import Review as ReviewModel
        review = self.db.query(ReviewModel).filter(ReviewModel.application_id == application_id).first()
        if not review:
            review = ReviewModel(application_id=application_id, reviewer_id=reviewer_id, **data)
            self.db.add(review)
        else:
            for key, value in data.items():
                setattr(review, key, value)
            review.reviewer_id = reviewer_id
        self.db.commit()
        self.db.refresh(review)
        return review

    def list_by_reviewer(self, reviewer_id: uuid.UUID):
        from app.models.review import Review as ReviewModel
        return self.db.query(ReviewModel).filter(ReviewModel.reviewer_id == reviewer_id).all() 