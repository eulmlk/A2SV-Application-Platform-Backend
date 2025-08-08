from typing import Optional
from datetime import datetime, date
import uuid


class Role:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name


class User:
    def __init__(
        self,
        id: uuid.UUID,
        email: str,
        password: str,
        full_name: str,
        role_id: int,
        created_at: datetime,
        updated_at: datetime,
        profile_picture_url: str = None,
        is_active: bool = True,
    ):
        self.id = id
        self.email = email
        self.password = password
        self.full_name = full_name
        self.role_id = role_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.profile_picture_url = profile_picture_url
        self.is_active = is_active


class ApplicationCycle:
    def __init__(
        self,
        id: int,
        name: str,
        start_date: date,
        end_date: date,
        is_active: bool,
        created_at: datetime,
        description: Optional[str] = None,
    ):
        self.id = id
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.is_active = is_active
        self.created_at = created_at
        self.description = description


class Application:
    def __init__(
        self,
        id: uuid.UUID,
        applicant_id: uuid.UUID,
        cycle_id: int,
        status: str,
        school: str,
        student_id: str,
        leetcode_handle: str,
        codeforces_handle: str,
        essay_why_a2sv: str,
        essay_about_you: str,
        resume_url: str,
        assigned_reviewer_id: Optional[uuid.UUID],
        decision_notes: Optional[str],
        updated_at: datetime,
        submitted_at: Optional[datetime],
        country: str,
        degree: str,
    ):
        self.id = id
        self.applicant_id = applicant_id
        self.cycle_id = cycle_id
        self.status = status
        self.school = school
        self.student_id = student_id
        self.leetcode_handle = leetcode_handle
        self.codeforces_handle = codeforces_handle
        self.essay_why_a2sv = essay_why_a2sv
        self.essay_about_you = essay_about_you
        self.resume_url = resume_url
        self.assigned_reviewer_id = assigned_reviewer_id
        self.decision_notes = decision_notes
        self.submitted_at = submitted_at
        self.updated_at = updated_at
        self.country = country
        self.degree = degree


class Review:
    def __init__(
        self,
        id: uuid.UUID,
        application_id: uuid.UUID,
        reviewer_id: Optional[uuid.UUID],
        activity_check_notes: Optional[str],
        resume_score: Optional[int],
        essay_score: Optional[int],
        technical_interview_score: Optional[int],
        behavioral_interview_score: Optional[int],
        interview_notes: Optional[str],
        created_at: datetime,
        updated_at: datetime,
    ):
        self.id = id
        self.application_id = application_id
        self.reviewer_id = reviewer_id
        self.activity_check_notes = activity_check_notes
        self.resume_score = resume_score
        self.essay_score = essay_score
        self.technical_interview_score = technical_interview_score
        self.behavioral_interview_score = behavioral_interview_score
        self.interview_notes = interview_notes
        self.created_at = created_at
        self.updated_at = updated_at


class Permission:
    def __init__(self, name: str):
        self.name = name
