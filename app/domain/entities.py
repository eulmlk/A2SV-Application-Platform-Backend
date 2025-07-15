from typing import Optional
from datetime import datetime, date
import uuid

class Role:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

class User:
    def __init__(self, id: uuid.UUID, email: str, password: str, full_name: str, role_id: int, created_at: datetime, updated_at: datetime):
        self.id = id
        self.email = email
        self.password = password
        self.full_name = full_name
        self.role_id = role_id
        self.created_at = created_at
        self.updated_at = updated_at

class ApplicationCycle:
    def __init__(self, id: int, name: str, start_date: date, end_date: date, is_active: bool, created_at: datetime):
        self.id = id
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.is_active = is_active
        self.created_at = created_at

class Application:
    def __init__(self, id: uuid.UUID, applicant_id: uuid.UUID, cycle_id: int, status: str, school: str, degree: str, leetcode_handle: str, codeforces_handle: str, essay: str, resume_url: str, assigned_reviewer_id: Optional[uuid.UUID], decision_notes: Optional[str], submitted_at: datetime, updated_at: datetime):
        self.id = id
        self.applicant_id = applicant_id
        self.cycle_id = cycle_id
        self.status = status
        self.school = school
        self.degree = degree
        self.leetcode_handle = leetcode_handle
        self.codeforces_handle = codeforces_handle
        self.essay = essay
        self.resume_url = resume_url
        self.assigned_reviewer_id = assigned_reviewer_id
        self.decision_notes = decision_notes
        self.submitted_at = submitted_at
        self.updated_at = updated_at

class Review:
    def __init__(self, id: uuid.UUID, application_id: uuid.UUID, reviewer_id: Optional[uuid.UUID], activity_check_notes: Optional[str], resume_score: Optional[int], essay_score: Optional[int], technical_interview_score: Optional[int], behavioral_interview_score: Optional[int], interview_notes: Optional[str], created_at: datetime, updated_at: datetime):
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