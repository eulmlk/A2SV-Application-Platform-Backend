from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.core.database import Base

class Application(Base):
    __tablename__ = "applications"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    applicant_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    cycle_id = Column(Integer, ForeignKey("application_cycles.id"), nullable=False)
    status = Column(String(50), nullable=False, default="in_progress")
    school = Column(String(255), nullable=False)
    student_id = Column(String(255), nullable=False)
    leetcode_handle = Column(String(100), nullable=False)
    codeforces_handle = Column(String(100), nullable=False)
    essay_why_a2sv = Column(Text, nullable=False)
    essay_about_you = Column(Text, nullable=False)
    resume_url = Column(String(512), nullable=False)
    assigned_reviewer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    decision_notes = Column(Text, nullable=True)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()) 