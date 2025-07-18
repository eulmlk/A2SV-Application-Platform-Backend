from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.schemas.application import ApplicationSubmitRequest, ApplicationResponse, ApplicationStatusResponse
from app.core.database import get_db
from app.repositories.sqlalchemy_impl import ApplicationRepository, ApplicationCycleRepository
from app.api.deps import applicant_required
from app.domain.entities import Application
from app.schemas.base import APIResponse
import uuid
import os
from datetime import datetime
import cloudinary.uploader  
import shutil

router = APIRouter(prefix="/applications", tags=["applications"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/", response_model=APIResponse[ApplicationResponse], status_code=201)
def create_application(
    school: str = Form(...),
    degree: str = Form(...),
    leetcode_handle: str = Form(...),
    codeforces_handle: str = Form(...),
    essay: str = Form(...),
    resume: UploadFile = File(...),
    current_user=Depends(applicant_required),
    db: Session = Depends(get_db)
):
    # All your initial checks are correct
    app_repo = ApplicationRepository(db)
    cycle_repo = ApplicationCycleRepository(db)
    active_cycle = cycle_repo.get_active()
    if not active_cycle:
        raise HTTPException(status_code=400, detail="No active application cycle found.")
    
    existing_application = app_repo.get_by_applicant_id(current_user.id)
    if existing_application:
        raise HTTPException(status_code=400, detail="You have already submitted an application.")
    
    if not resume.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Resume must be a PDF file.")

    temp_file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{resume.filename}")
    
    try:
        # Save the uploaded file stream to a stable temporary file
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(resume.file, buffer)

        # Upload the stable local file to Cloudinary
        result = cloudinary.uploader.upload(
            temp_file_path,
            resource_type="raw",
            folder="resumes",
        )
        resume_url = result["secure_url"]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload process failed: {str(e)}")
    
    finally:
        # THE FIX IS HERE: We DO NOT close the resume.file stream.
        # FastAPI/Starlette will manage its lifecycle.
        # We only need to clean up the temporary file we created ourselves.
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

    # The rest of your code is correct and remains unchanged...
    application = Application(
        id=uuid.uuid4(),
        applicant_id=current_user.id,
        cycle_id=active_cycle.id,
        status="in_progress",
        school=school,
        degree=degree,
        leetcode_handle=leetcode_handle,
        codeforces_handle=codeforces_handle,
        essay=essay,
        resume_url=resume_url,
        assigned_reviewer_id=None,
        decision_notes=None,
        submitted_at=None,
        updated_at=datetime.utcnow()
    )
    app = app_repo.create(application)

    response_data =  ApplicationResponse(
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

    return APIResponse(
        data=response_data,
        message="Application submitted successfully",
        success=True,
    )

@router.get("/my-status/", response_model=APIResponse[ApplicationStatusResponse])
def get_my_status(current_user = Depends(applicant_required), db: Session = Depends(get_db)):
    app_repo = ApplicationRepository(db)
    app = app_repo.get_by_applicant_id(current_user.id)
    if not app:
        raise HTTPException(status_code=404, detail="No application found.")
    response_data = ApplicationStatusResponse(
        id=str(app.id),
        status=app.status,
        school=app.school,
        submitted_at=app.submitted_at
    )
    
    return APIResponse(
        data=response_data,
        message="Application status fetched successfully",
        success=True,
    )


@router.get("/{application_id}/", response_model=APIResponse[ApplicationResponse])
def get_application(application_id: str, current_user = Depends(applicant_required), db: Session = Depends(get_db)):
    app_repo = ApplicationRepository(db)

    try:
        app = app_repo.get_by_id(uuid.UUID(application_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid application ID.")
    
    if not app:
        raise HTTPException(status_code=404, detail="Application not found.")
    
    if app.applicant_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to access this application.")
    
    response_data = ApplicationResponse(
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
    
    return APIResponse(
        data=response_data,
        message="Application fetched successfully",
        success=True,
    )


@router.put("/{application_id}/", response_model=APIResponse[ApplicationResponse])
def update_application(application_id: str, current_user = Depends(applicant_required), db: Session = Depends(get_db)):
    app_repo = ApplicationRepository(db)
    app = app_repo.get_by_id(uuid.UUID(application_id))
    if not app:
        raise HTTPException(status_code=404, detail="Application not found.")
    
    if app.applicant_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to update this application.")

    if app.status != "in_progress":
        raise HTTPException(status_code=400, detail="You can only update your application before it is submitted.")

    app_repo.update(app)

    response_data = ApplicationResponse(
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

    return APIResponse(
        data=response_data,
        message="Application updated successfully",
        success=True,
    )

@router.delete("/{application_id}/", response_model=APIResponse[ApplicationResponse])
def delete_application(application_id: str, current_user = Depends(applicant_required), db: Session = Depends(get_db)):
    app_repo = ApplicationRepository(db)
    app = app_repo.get_by_id(uuid.UUID(application_id))
    if not app:
        raise HTTPException(status_code=404, detail="Application not found.")
    
    if app.applicant_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to delete this application.")

    if app.status != "in_progress":
        raise HTTPException(status_code=400, detail="You can only delete your application before it is submitted.")

    app_repo.delete(app.id)
    
    return APIResponse(
        data=None,
        message="Application deleted successfully",
        success=True,
    )

@router.patch("/{application_id}/", response_model=APIResponse[ApplicationResponse])
def submit_application(application_id: str, current_user = Depends(applicant_required), db: Session = Depends(get_db)):
    app_repo = ApplicationRepository(db)
    app = app_repo.get_by_id(uuid.UUID(application_id))
    if not app:
        raise HTTPException(status_code=404, detail="Application not found.")
    
    if app.applicant_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to submit this application.")
    
    if app.status != "in_progress":
        raise HTTPException(status_code=400, detail="You have already submitted your application.")

    app.status = "submitted"
    app.submitted_at = datetime.utcnow()
    app_repo.update(app)

    response_data = ApplicationResponse(
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

    return APIResponse(
        data=response_data,
        message="Application submitted successfully",
        success=True,
    )