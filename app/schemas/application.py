from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ApplicationSubmitRequest(BaseModel):
    school: str
    degree: str
    leetcode_handle: str
    codeforces_handle: str
    essay: str
    # resume: file upload handled separately

class ApplicationResponse(BaseModel):
    id: str
    status: str
    school: str
    degree: str
    leetcode_handle: str
    codeforces_handle: str
    essay: str
    resume_url: str
    submitted_at: Optional[datetime]
    updated_at: datetime

class ApplicationStatusResponse(BaseModel):
    id: str
    status: str
    school: str
    submitted_at: Optional[datetime] 