from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.core.database import Base

class Review(Base):
    __tablename__ = "reviews"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id"), unique=True, nullable=False)
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    activity_check_notes = Column(Text, nullable=True)
    resume_score = Column(Integer, nullable=True)
    essay_why_a2sv_score = Column(Integer, nullable=True)
    essay_about_you_score = Column(Integer, nullable=True)
    technical_interview_score = Column(Integer, nullable=True)
    behavioral_interview_score = Column(Integer, nullable=True)
    interview_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()) 