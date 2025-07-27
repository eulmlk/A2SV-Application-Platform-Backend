from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ApplicationSubmitRequest(BaseModel):
    school: str
    degree: str
    leetcode_handle: str
    codeforces_handle: str
    essay_why_a2sv: str
    essay_about_you: str

class ApplicationResponse(BaseModel):
    id: str
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

class ApplicationStatusResponse(BaseModel):
    id: str
    status: str
    school: str
    submitted_at: Optional[datetime] 