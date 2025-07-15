from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.schemas.application import ApplicationSubmitRequest, ApplicationResponse, ApplicationStatusResponse
from app.core.database import get_db
from app.repositories.sqlalchemy_impl import ApplicationRepository
from app.api.deps import applicant_required
from app.domain.entities import Application
import uuid
import os
from datetime import datetime

router = APIRouter(prefix="/applications", tags=["applications"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/", response_model=ApplicationResponse, status_code=201)
def submit_application(
    school: str = Form(...),
    degree: str = Form(...),
    leetcode_handle: str = Form(...),
    codeforces_handle: str = Form(...),
    essay: str = Form(...),
    resume: UploadFile = File(...),
    current_user = Depends(applicant_required),
    db: Session = Depends(get_db)
):
    app_repo = ApplicationRepository(db)
    # Save resume file
    filename = f"{uuid.uuid4()}_{resume.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(resume.file.read())
    resume_url = f"/static/{filename}"
    # Create application
    application = Application(
        id=uuid.uuid4(),
        applicant_id=current_user.id,
        cycle_id=1,  # TODO: fetch active cycle
        status="Submitted",
        school=school,
        degree=degree,
        leetcode_handle=leetcode_handle,
        codeforces_handle=codeforces_handle,
        essay=essay,
        resume_url=resume_url,
        assigned_reviewer_id=None,
        decision_notes=None,
        submitted_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    app = app_repo.create(application)
    return ApplicationResponse(
        id=str(app.id),
        status=app.status,
        school=app.school,
        degree=app.degree,
        leetcode_handle=app.leetcode_handle,
        codeforces_handle=app.codeforces_handle,
        essay=app.essay,
        resume_url=app.resume_url,
        submitted_at=app.submitted_at,
        updated_at=app.updated_at
    )

@router.get("/my-status/", response_model=ApplicationStatusResponse)
def get_my_status(current_user = Depends(applicant_required), db: Session = Depends(get_db)):
    app_repo = ApplicationRepository(db)
    app = app_repo.get_by_applicant_id(current_user.id)
    if not app:
        raise HTTPException(status_code=404, detail="No application found.")
    return ApplicationStatusResponse(
        id=str(app.id),
        status=app.status,
        school=app.school,
        submitted_at=app.submitted_at
    ) 