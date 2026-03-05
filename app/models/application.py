from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    status = Column(String, default="applied")
    # Status flow: applied → shortlisted → interview → selected → rejected | placed
    match_percentage = Column(Float, default=0.0)
    missing_skills = Column(JSON, default=list)
    ai_roadmap = Column(JSON, nullable=True)  # Stored AI response
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    notes = Column(String, nullable=True)  # Admin/Company notes

    student = relationship("Student", back_populates="applications")
    job = relationship("Job", back_populates="applications")
