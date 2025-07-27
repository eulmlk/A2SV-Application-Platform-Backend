from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.sqlalchemy_impl import (
    ApplicationRepository,
    ReviewRepository,
    UserRepository,
)
from app.schemas.base import APIResponse
import uuid
from app.core.security import require_token_type
from fastapi.security import HTTPAuthorizationCredentials
from app.api.auth import bearer_scheme
from app.api.deps import reviewer_required
from app.schemas.review import (
    AssignedApplicationSummary,
    ApplicationWithReview,
    ReviewDetail,
    ReviewUpdateRequest,
    FullApplication,
)

router = APIRouter(prefix="/reviews", tags=["reviews"])


# Helper to extract and validate access token from credentials
def get_access_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    return require_token_type(credentials.credentials, "access")


@router.get("/assigned/", response_model=APIResponse[list[AssignedApplicationSummary]])
def list_assigned_applications(
    current_user=Depends(reviewer_required),
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    get_access_token_payload(credentials)
    app_repo = ApplicationRepository(db)
    user_repo = UserRepository(db)
    apps = app_repo.list_by_reviewer(current_user.id)
    summaries = []
    for app in apps:
        applicant = user_repo.get_by_id(app.applicant_id)
        summaries.append(
            AssignedApplicationSummary(
                application_id=str(app.id),
                applicant_name=applicant.full_name if applicant else "",
                status=app.status,
                submission_date=app.submitted_at,
            )
        )
    return APIResponse(data=summaries, message="Assigned applications retrieved.")


@router.get(
    "/{application_id}/", response_model=APIResponse[ApplicationWithReview]
)  # Changed response model
def get_application_review(
    application_id: str,
    current_user=Depends(reviewer_required),
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    get_access_token_payload(credentials)
    app_repo = ApplicationRepository(db)
    review_repo = ReviewRepository(db)
    user_repo = UserRepository(db)
    try:
        app = app_repo.get_by_id(uuid.UUID(application_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid application ID.")
    if not app:
        raise HTTPException(status_code=404, detail="Application not found.")
    if app.assigned_reviewer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not assigned to this application.")
    applicant = user_repo.get_by_id(app.applicant_id)

    # Create the FullApplication object with data from the 'app' object
    full_application = FullApplication(
        id=str(app.id),
        applicant_name=applicant.full_name if applicant else "",
        status=app.status,
        school=app.school,
        degree=app.degree,
        leetcode_handle=app.leetcode_handle,
        codeforces_handle=app.codeforces_handle,
        essay_why_a2sv=app.essay_why_a2sv,
        essay_about_you=app.essay_about_you,
        resume_url=app.resume_url,
        submitted_at=app.submitted_at,
        updated_at=app.updated_at,
    )

    review = review_repo.get_by_application_id(app.id)
    review_detail = None
    if review:
        review_detail = ReviewDetail(
            id=str(review.id),
            application_id=str(review.application_id),
            reviewer_id=str(review.reviewer_id) if review.reviewer_id else None,
            activity_check_notes=review.activity_check_notes,
            resume_score=review.resume_score,
            essay_why_a2sv_score=review.essay_why_a2sv_score,
            essay_about_you_score=review.essay_about_you_score,
            technical_interview_score=review.technical_interview_score,
            behavioral_interview_score=review.behavioral_interview_score,
            interview_notes=review.interview_notes,
            created_at=review.created_at,
            updated_at=review.updated_at,
        )

    app_with_review = ApplicationWithReview(
        id=str(app.id),
        applicant_details=full_application,  # Use the populated FullApplication object
        review_details=review_detail,  # Use the populated ReviewDetail object
    )
    return APIResponse(
        data=app_with_review, message="Application and review details retrieved."
    )


@router.put("/{application_id}/", response_model=APIResponse[ReviewDetail])
def update_review(
    application_id: str,
    data: ReviewUpdateRequest,
    current_user=Depends(reviewer_required),
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    get_access_token_payload(credentials)
    app_repo = ApplicationRepository(db)
    review_repo = ReviewRepository(db)
    try:
        app = app_repo.get_by_id(uuid.UUID(application_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid application ID.")
    if not app:
        raise HTTPException(status_code=404, detail="Application not found.")
    if app.assigned_reviewer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not assigned to this application.")
    review = review_repo.create_or_update(
        app.id, current_user.id, data.dict(exclude_unset=True)
    )
    review_detail = ReviewDetail(
        id=str(review.id),
        application_id=str(review.application_id),
        reviewer_id=str(review.reviewer_id) if review.reviewer_id else None,
        activity_check_notes=review.activity_check_notes,
        resume_score=review.resume_score,
        essay_why_a2sv_score=review.essay_why_a2sv_score,
        essay_about_you_score=review.essay_about_you_score,
        technical_interview_score=review.technical_interview_score,
        behavioral_interview_score=review.behavioral_interview_score,
        interview_notes=review.interview_notes,
        created_at=review.created_at,
        updated_at=review.updated_at,
    )

    return APIResponse(data=review_detail, message="Review updated.")
