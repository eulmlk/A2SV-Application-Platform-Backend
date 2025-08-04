from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class AssignedApplicationSummary(BaseModel):
    application_id: str
    applicant_name: str
    status: str
    submission_date: Optional[datetime]


class FullApplication(BaseModel):
    id: str
    applicant_name: str
    status: str
    school: str
    degree: str
    leetcode_handle: str
    codeforces_handle: str
    essay_why_a2sv: str
    essay_about_you: str
    resume_url: str
    submitted_at: Optional[datetime]
    updated_at: datetime


class ReviewDetail(BaseModel):
    id: str
    application_id: str
    reviewer_id: Optional[str]
    activity_check_notes: Optional[str]
    resume_score: Optional[int]
    essay_why_a2sv_score: Optional[int]
    essay_about_you_score: Optional[int]
    technical_interview_score: Optional[int]
    behavioral_interview_score: Optional[int]
    interview_notes: Optional[str]
    created_at: datetime
    updated_at: datetime


class ApplicationWithReview(BaseModel):
    id: str
    applicant_details: FullApplication
    review_details: Optional[ReviewDetail]


class ReviewUpdateRequest(BaseModel):
    activity_check_notes: Optional[str]
    resume_score: Optional[int]
    essay_why_a2sv_score: Optional[int]
    essay_about_you_score: Optional[int]
    technical_interview_score: Optional[int]
    behavioral_interview_score: Optional[int]
    interview_notes: Optional[str]


class ReviewListResponse(BaseModel):
    reviews: List[AssignedApplicationSummary]
    total_count: int
    page: int
    limit: int
