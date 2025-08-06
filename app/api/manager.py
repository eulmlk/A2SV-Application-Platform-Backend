from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from app.domain.entities import User
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.sqlalchemy_impl import (
    ApplicationRepository,
    ApplicationCycleRepository,
    UserRepository,
)
from app.models.application import Application as ApplicationModel
from app.schemas.application import ApplicationResponse
from app.api.auth import bearer_scheme
from app.core.security import require_token_type
from fastapi.security import HTTPAuthorizationCredentials
from app.schemas.base import APIResponse
from app.api.deps import manager_required
import logging

router = APIRouter(
    prefix="/manager/applications",
    tags=["managers"],
    dependencies=[
        Depends(bearer_scheme)
    ],  # <-- This makes endpoints "locked" in Swagger UI
)


# Helper to extract and validate access token from credentials
def get_access_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    return require_token_type(credentials.credentials, "access")


# Response model for GET /manager/applications/
class ApplicationSummary(BaseModel):
    id: UUID
    applicant_name: str
    status: str
    assigned_reviewer_name: Optional[str]


class ApplicationListResponse(BaseModel):
    applications: List[ApplicationSummary]
    total_count: int
    page: int
    limit: int


# Request/response models for PATCH endpoints
class AssignReviewerRequest(BaseModel):
    reviewer_id: UUID


class AssignReviewerResponse(BaseModel):
    message: str


class DecideRequest(BaseModel):
    status: str  # Should be 'Accepted' or 'Rejected'
    decision_notes: Optional[str]


# GET /manager/applications/
@router.get("/", response_model=APIResponse[ApplicationListResponse])
def list_applications(
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(manager_required),
    db: Session = Depends(get_db),
):
    app_repo = ApplicationRepository(db)
    cycle_repo = ApplicationCycleRepository(db)
    user_repo = UserRepository(db)
    active_cycle = cycle_repo.get_active()
    if not active_cycle:
        return APIResponse(
            data=ApplicationListResponse(
                applications=[], total_count=0, page=page, limit=limit
            ),
            message="No active cycle found",
        )

    # Query all applications for the active cycle, optionally filter by status
    query = db.query(ApplicationModel).filter(
        ApplicationModel.cycle_id == active_cycle.id
    )
    if status:
        query = query.filter(ApplicationModel.status == status)

    # Get total count for pagination
    total_count = query.count()

    # Apply pagination
    offset = (page - 1) * limit
    apps = query.offset(offset).limit(limit).all()

    results = []
    for app in apps:
        applicant = user_repo.get_by_id(app.applicant_id)
        reviewer_name = None
        if app.assigned_reviewer_id:
            reviewer = user_repo.get_by_id(app.assigned_reviewer_id)
            reviewer_name = reviewer.full_name if reviewer else None
        results.append(
            ApplicationSummary(
                id=app.id,
                applicant_name=applicant.full_name if applicant else "",
                status=app.status,
                assigned_reviewer_name=reviewer_name,
            )
        )

    response_data = ApplicationListResponse(
        applications=results, total_count=total_count, page=page, limit=limit
    )
    return APIResponse(data=response_data, message="Applications fetched successfully")


# GET /manager/applications/{application_id}/
@router.get("/{application_id}/", response_model=APIResponse[ApplicationResponse])
def get_application(
    application_id: UUID,
    current_user: User = Depends(manager_required),
    db: Session = Depends(get_db),
):
    app_repo = ApplicationRepository(db)
    application = app_repo.get_by_id(application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    response_data = ApplicationResponse(
        id=str(application.id),
        status=application.status,
        school=application.school,
        student_id=application.student_id,
        country=application.country,
        degree=application.degree,
        leetcode_handle=application.leetcode_handle,
        codeforces_handle=application.codeforces_handle,
        essay_why_a2sv=application.essay_why_a2sv,
        essay_about_you=application.essay_about_you,
        resume_url=application.resume_url,
        submitted_at=application.submitted_at,
        updated_at=application.updated_at,
    )
    return APIResponse(data=response_data, message="Application fetched successfully")


# PATCH /manager/applications/{application_id}/assign/
@router.patch("/{application_id}/assign/", response_model=APIResponse[None])
def assign_reviewer(
    application_id: UUID,
    req: AssignReviewerRequest,
    current_user: User = Depends(manager_required),
    db: Session = Depends(get_db),
):
    logging.info(
        f"Assign Reviewer called with application_id={application_id}, reviewer_id={req.reviewer_id}"
    )

    app_repo = ApplicationRepository(db)
    user_repo = UserRepository(db)

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
        application.status = "pending_review"
        app_repo.update(application)
        logging.info(
            f"Reviewer {req.reviewer_id} assigned to application {application_id}"
        )
    except Exception as e:
        logging.error(f"Error assigning reviewer: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

    return APIResponse(message="Reviewer assigned successfully.")


# PATCH /manager/applications/{application_id}/decide/
@router.patch("/{application_id}/decide/", response_model=APIResponse[None])
def decide_application(
    application_id: UUID,
    req: DecideRequest,
    current_user: User = Depends(manager_required),
    db: Session = Depends(get_db),
):
    if req.status not in ["accepted", "rejected"]:
        raise HTTPException(
            status_code=400, detail="Status must be 'accepted' or 'rejected'."
        )

    app_repo = ApplicationRepository(db)
    application = app_repo.get_by_id(application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    application.status = req.status
    application.decision_notes = req.decision_notes
    app_repo.update(application)
    return APIResponse(message="Decision recorded successfully.")
