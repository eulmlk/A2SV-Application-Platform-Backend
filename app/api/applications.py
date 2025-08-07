from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.schemas.application import (
    ApplicationResponse,
    ApplicationStatusResponse,
)
from app.core.database import get_db
from app.repositories.sqlalchemy_impl import (
    ApplicationRepository,
    ApplicationCycleRepository,
)
from app.api.deps import applicant_required
from app.domain.entities import Application
from app.schemas.base import APIResponse
from app.core.utils import (
    raise_not_found,
    raise_forbidden,
    raise_conflict,
    raise_validation_error,
    raise_internal_error,
)
import uuid
import os
from datetime import datetime
import cloudinary.uploader
import shutil

# Import bearer_scheme from auth.py
from app.api.auth import bearer_scheme
from app.core.security import require_token_type
from fastapi.security import HTTPAuthorizationCredentials

router = APIRouter(prefix="/applications", tags=["applications"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# Helper to extract and validate access token from credentials
def get_access_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    return require_token_type(credentials.credentials, "access")


@router.post(
    "/",
    response_model=APIResponse[ApplicationResponse],
    status_code=201,
    dependencies=[Depends(bearer_scheme)],
)
def create_application(
    school: str = Form(...),
    student_id: str = Form(...),
    country: str = Form(...),
    degree: str = Form(...),
    leetcode_handle: str = Form(...),
    codeforces_handle: str = Form(...),
    essay_why_a2sv: str = Form(...),
    essay_about_you: str = Form(...),
    resume: UploadFile = File(...),
    current_user=Depends(applicant_required),
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    get_access_token_payload(credentials)
    app_repo = ApplicationRepository(db)
    cycle_repo = ApplicationCycleRepository(db)
    active_cycle = cycle_repo.get_active()
    if not active_cycle:
        raise_validation_error("No active application cycle found.")

    existing_application = app_repo.get_by_applicant_id(current_user.id)
    if existing_application:
        raise_conflict("You have already submitted an application.")

    if not resume.filename.endswith(".pdf"):
        raise_validation_error("Resume must be a PDF file.")

    temp_file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{resume.filename}")

    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(resume.file, buffer)
        result = cloudinary.uploader.upload(
            temp_file_path,
            resource_type="raw",
            folder="resumes",
        )
        resume_url = result["secure_url"]
    except Exception as e:
        raise_internal_error(f"File upload process failed: {str(e)}")
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

    application = Application(
        id=uuid.uuid4(),
        applicant_id=current_user.id,
        cycle_id=active_cycle.id,
        status="in_progress",
        school=school,
        student_id=student_id,
        country=country,
        degree=degree,
        leetcode_handle=leetcode_handle,
        codeforces_handle=codeforces_handle,
        essay_why_a2sv=essay_why_a2sv,
        essay_about_you=essay_about_you,
        resume_url=resume_url,
        assigned_reviewer_id=None,
        decision_notes=None,
        submitted_at=None,
        updated_at=datetime.utcnow(),
    )
    app = app_repo.create(application)

    response_data = ApplicationResponse(
        id=str(app.id),
        status=app.status,
        school=app.school,
        student_id=app.student_id,
        country=app.country,
        degree=app.degree,
        leetcode_handle=app.leetcode_handle,
        codeforces_handle=app.codeforces_handle,
        essay_why_a2sv=app.essay_why_a2sv,
        essay_about_you=app.essay_about_you,
        resume_url=app.resume_url,
        submitted_at=app.submitted_at,
        updated_at=app.updated_at,
    )

    return APIResponse(
        data=response_data,
        message="Application submitted successfully",
        success=True,
    )


@router.get(
    "/my-status/",
    response_model=APIResponse[ApplicationStatusResponse],
    dependencies=[Depends(bearer_scheme)],
)
def get_my_status(
    current_user=Depends(applicant_required),
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    get_access_token_payload(credentials)
    app_repo = ApplicationRepository(db)
    app = app_repo.get_by_applicant_id(current_user.id)
    if not app:
        raise_not_found("No application found.", "application")
    response_data = ApplicationStatusResponse(
        id=str(app.id),
        status=app.status,
        school=app.school,
        country=app.country,
        degree=app.degree,
        submitted_at=app.submitted_at,
    )
    return APIResponse(
        data=response_data,
        message="Application status fetched successfully",
        success=True,
    )


@router.get(
    "/{application_id}/",
    response_model=APIResponse[ApplicationResponse],
    dependencies=[Depends(bearer_scheme)],
)
def get_application(
    application_id: str,
    current_user=Depends(applicant_required),
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    get_access_token_payload(credentials)
    app_repo = ApplicationRepository(db)
    try:
        app = app_repo.get_by_id(uuid.UUID(application_id))
    except ValueError:
        raise_validation_error("Invalid application ID.")
    if not app:
        raise_not_found("Application not found.", "application")
    if app.applicant_id != current_user.id:
        raise_forbidden("You are not authorized to access this application.")
    response_data = ApplicationResponse(
        id=str(app.id),
        status=app.status,
        school=app.school,
        student_id=app.student_id,
        country=app.country,
        degree=app.degree,
        leetcode_handle=app.leetcode_handle,
        codeforces_handle=app.codeforces_handle,
        essay_why_a2sv=app.essay_why_a2sv,
        essay_about_you=app.essay_about_you,
        resume_url=app.resume_url,
        submitted_at=app.submitted_at,
        updated_at=app.updated_at,
    )
    return APIResponse(
        data=response_data,
        message="Application fetched successfully",
        success=True,
    )


@router.put(
    "/{application_id}/",
    response_model=APIResponse[ApplicationResponse],
    dependencies=[Depends(bearer_scheme)],
)
def update_application(
    application_id: str,
    current_user=Depends(applicant_required),
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    school: str = Form(None),
    student_id: str = Form(None),
    country: str = Form(None),
    leetcode_handle: str = Form(None),
    codeforces_handle: str = Form(None),
    essay_why_a2sv: str = Form(None),
    essay_about_you: str = Form(None),
    resume: UploadFile = File(None),
):
    get_access_token_payload(credentials)
    app_repo = ApplicationRepository(db)
    app = app_repo.get_by_id(uuid.UUID(application_id))
    if not app:
        raise_not_found("Application not found.", "application")
    if app.applicant_id != current_user.id:
        raise_forbidden("You are not authorized to update this application.")
    if app.status != "in_progress":
        raise_conflict("You can only update your application before it is submitted.")

    if school is not None:
        app.school = school
    if student_id is not None:
        app.student_id = student_id
    if country is not None:
        app.country = country
    if leetcode_handle is not None:
        app.leetcode_handle = leetcode_handle
    if codeforces_handle is not None:
        app.codeforces_handle = codeforces_handle
    if essay_why_a2sv is not None:
        app.essay_why_a2sv = essay_why_a2sv
    if essay_about_you is not None:
        app.essay_about_you = essay_about_you

    if resume is not None:
        if not resume.filename.endswith(".pdf"):
            raise_validation_error("Resume must be a PDF file.")
        temp_file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{resume.filename}")
        try:
            with open(temp_file_path, "wb") as buffer:
                shutil.copyfileobj(resume.file, buffer)
            result = cloudinary.uploader.upload(
                temp_file_path,
                resource_type="raw",
                folder="resumes",
            )
            resume_url = result["secure_url"]
            app.resume_url = resume_url
        except Exception as e:
            raise_internal_error(f"File upload process failed: {str(e)}")
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    app_repo.update(app)
    response_data = ApplicationResponse(
        id=str(app.id),
        status=app.status,
        school=app.school,
        student_id=app.student_id,
        country=app.country,
        degree=app.degree,
        leetcode_handle=app.leetcode_handle,
        codeforces_handle=app.codeforces_handle,
        essay_why_a2sv=app.essay_why_a2sv,
        essay_about_you=app.essay_about_you,
        resume_url=app.resume_url,
        submitted_at=app.submitted_at,
        updated_at=app.updated_at,
    )

    return APIResponse(
        data=response_data,
        message="Application updated successfully",
        success=True,
    )


@router.delete(
    "/{application_id}/",
    response_model=APIResponse[ApplicationResponse],
    dependencies=[Depends(bearer_scheme)],
)
def delete_application(
    application_id: str,
    current_user=Depends(applicant_required),
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    get_access_token_payload(credentials)
    app_repo = ApplicationRepository(db)
    app = app_repo.get_by_id(uuid.UUID(application_id))
    if not app:
        raise_not_found("Application not found.", "application")
    if app.applicant_id != current_user.id:
        raise_forbidden("You are not authorized to delete this application.")
    if app.status != "in_progress":
        raise_conflict("You can only delete your application before it is submitted.")
    app_repo.delete(app.id)
    return APIResponse(
        data=None,
        message="Application deleted successfully",
        success=True,
    )


@router.patch(
    "/{application_id}/",
    response_model=APIResponse[ApplicationResponse],
    dependencies=[Depends(bearer_scheme)],
)
def submit_application(
    application_id: str,
    current_user=Depends(applicant_required),
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    get_access_token_payload(credentials)
    app_repo = ApplicationRepository(db)
    app = app_repo.get_by_id(uuid.UUID(application_id))
    if not app:
        raise_not_found("Application not found.", "application")
    if app.applicant_id != current_user.id:
        raise_forbidden("You are not authorized to submit this application.")
    if app.status != "in_progress":
        raise_conflict("You have already submitted your application.")
    app.status = "submitted"
    app.submitted_at = datetime.utcnow()
    app_repo.update(app)
    response_data = ApplicationResponse(
        id=str(app.id),
        status=app.status,
        school=app.school,
        student_id=app.student_id,
        country=app.country,
        degree=app.degree,
        leetcode_handle=app.leetcode_handle,
        codeforces_handle=app.codeforces_handle,
        essay_why_a2sv=app.essay_why_a2sv,
        essay_about_you=app.essay_about_you,
        resume_url=app.resume_url,
        submitted_at=app.submitted_at,
        updated_at=app.updated_at,
    )
    return APIResponse(
        data=response_data,
        message="Application submitted successfully",
        success=True,
    )
