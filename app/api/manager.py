from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from app.api import deps
from app.domain.entities import Application, User
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.sqlalchemy_impl import ApplicationRepository, ApplicationCycleRepository, UserRepository
from app.models.application import Application as ApplicationModel
from datetime import datetime
from app.api.auth import bearer_scheme  # Import your bearer_scheme
import logging

router = APIRouter(
    prefix="/manager/applications",
    tags=["Manager"],
    dependencies=[Depends(bearer_scheme)]  # <-- This makes endpoints "locked" in Swagger UI
)

# Manager RBAC guard
def manager_required(current_user: User = Depends(deps.get_current_user)):
    if current_user.role_id != 3:
        raise HTTPException(status_code=403, detail="Manager access required.")
    return current_user

# Response model for GET /manager/applications/
class ApplicationSummary(BaseModel):
    id: UUID
    applicant_name: str
    status: str
    assigned_reviewer_name: Optional[str]

# Request/response models for PATCH endpoints
class AssignReviewerRequest(BaseModel):
    reviewer_id: UUID

class AssignReviewerResponse(BaseModel):
    message: str

class DecideRequest(BaseModel):
    status: str  # Should be 'Accepted' or 'Rejected'
    decision_notes: Optional[str]

class DecideResponse(BaseModel):
    message: str

class ApplicationDetailResponse(BaseModel):
    id: UUID
    applicant_id: UUID
    cycle_id: int
    status: str
    school: str
    degree: str
    leetcode_handle: str
    codeforces_handle: str
    essay: str
    resume_url: str
    assigned_reviewer_id: Optional[UUID]
    decision_notes: Optional[str]
    submitted_at: Optional[datetime]
    updated_at: datetime

    class Config:
        orm_mode = True

# GET /manager/applications/
@router.get("/", response_model=List[ApplicationSummary])
def list_applications(status: Optional[str] = None, current_user: User = Depends(manager_required), db: Session = Depends(get_db)):
    app_repo = ApplicationRepository(db)
    cycle_repo = ApplicationCycleRepository(db)
    user_repo = UserRepository(db)
    active_cycle = cycle_repo.get_active()
    if not active_cycle:
        return []
    # Query all applications for the active cycle, optionally filter by status
    query = db.query(ApplicationModel).filter(ApplicationModel.cycle_id == active_cycle.id)
    if status:
        query = query.filter(ApplicationModel.status == status)
    apps = query.all()
    results = []
    for app in apps:
        applicant = user_repo.get_by_id(app.applicant_id)
        reviewer_name = None
        if app.assigned_reviewer_id:
            reviewer = user_repo.get_by_id(app.assigned_reviewer_id)
            reviewer_name = reviewer.full_name if reviewer else None
        results.append(ApplicationSummary(
            id=app.id,
            applicant_name=applicant.full_name if applicant else "",
            status=app.status,
            assigned_reviewer_name=reviewer_name
        ))
    return results

# GET /manager/applications/{application_id}/
@router.get("/{application_id}/", response_model=ApplicationDetailResponse)
def get_application(application_id: UUID, current_user: User = Depends(manager_required), db: Session = Depends(get_db)):
    app_repo = ApplicationRepository(db)
    application = app_repo.get_by_id(application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return application

# PATCH /manager/applications/{application_id}/assign/
@router.patch("/{application_id}/assign/", response_model=AssignReviewerResponse)
def assign_reviewer(
    application_id: UUID,
    req: AssignReviewerRequest,
    current_user: User = Depends(manager_required),
    db: Session = Depends(get_db)
):
    logging.info(f"Assign Reviewer called with application_id={application_id}, reviewer_id={req.reviewer_id}")

    app_repo = ApplicationRepository(db)
    user_repo = UserRepository(db)  # <-- ADD THIS LINE

    application = app_repo.get_by_id(application_id)
    if not application:
        logging.warning(f"Application with id {application_id} not found.")
        raise HTTPException(status_code=404, detail="Application not found")

    reviewer = user_repo.get_by_id(req.reviewer_id)
    if not reviewer:
        logging.warning(f"Reviewer with id {req.reviewer_id} not found.")
        raise HTTPException(status_code=404, detail="Reviewer not found")

    try:
        application.assigned_reviewer_id = req.reviewer_id
        app_repo.update(application)
        logging.info(f"Reviewer {req.reviewer_id} assigned to application {application_id}")
    except Exception as e:
        logging.error(f"Error assigning reviewer: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

    return {
        "message": "Reviewer assigned successfully.",
        "debug": {
            "application_id": str(application_id),
            "reviewer_id": str(req.reviewer_id)
        }
    }

# PATCH /manager/applications/{application_id}/decide/
@router.patch("/{application_id}/decide/", response_model=DecideResponse)
def decide_application(application_id: UUID, req: DecideRequest, current_user: User = Depends(manager_required), db: Session = Depends(get_db)):
    if req.status not in ["Accepted", "Rejected"]:
        raise HTTPException(status_code=400, detail="Status must be 'Accepted' or 'Rejected'.")
    app_repo = ApplicationRepository(db)
    application = app_repo.get_by_id(application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    application.status = req.status
    application.decision_notes = req.decision_notes
    app_repo.update(application)
    return {"message": "Decision recorded successfully."}