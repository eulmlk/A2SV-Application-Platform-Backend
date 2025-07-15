from sqlalchemy.orm import Session
from app.domain.entities import User, Application
from app.models.user import User as UserModel
from app.models.application import Application as ApplicationModel
from app.repositories.interfaces import IUserRepository, IApplicationRepository
import uuid

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
                essay=app.essay,
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
                essay=app.essay,
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
            essay=application.essay,
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
            essay=db_app.essay,
            resume_url=db_app.resume_url,
            assigned_reviewer_id=db_app.assigned_reviewer_id,
            decision_notes=db_app.decision_notes,
            submitted_at=db_app.submitted_at,
            updated_at=db_app.updated_at
        )

    def list_by_reviewer(self, reviewer_id: uuid.UUID):
        return []  # Not needed for applicant workflow

    def list_by_status(self, status: str):
        return []  # Not needed for applicant workflow

    def assign_reviewer(self, application_id: uuid.UUID, reviewer_id: uuid.UUID):
        return None  # Not needed for applicant workflow

    def finalize_decision(self, application_id: uuid.UUID, status: str, decision_notes: str):
        return None  # Not needed for applicant workflow

    def list_all(self):
        return []  # Not needed for applicant workflow 