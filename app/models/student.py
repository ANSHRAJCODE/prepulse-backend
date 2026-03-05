from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    roll_number = Column(String, unique=True, index=True)
    department = Column(String)
    batch_year = Column(Integer)
    cgpa = Column(Float, default=0.0)
    skills = Column(JSON, default=list)          # ["Python", "React", "SQL"]
    certifications = Column(JSON, default=list)  # ["AWS", "GCP"]
    projects = Column(JSON, default=list)        # [{"name": "x", "tech": ["React"]}]
    resume_url = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    github_url = Column(String, nullable=True)
    placement_status = Column(String, default="unplaced")  # unplaced, placed, opted_out
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="student_profile")
    applications = relationship("Application", back_populates="student")
