from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    company_name = Column(String, nullable=False)
    industry = Column(String)
    website = Column(String)
    description = Column(String)
    logo_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="company_profile")
    jobs = relationship("Job", back_populates="company")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    role_type = Column(String, default="full_time")  # full_time, internship
    required_skills = Column(JSON, default=list)      # ["Python", "Django"]
    preferred_skills = Column(JSON, default=list)     # ["Docker", "AWS"]
    min_cgpa = Column(Float, default=6.0)
    allowed_branches = Column(JSON, default=list)     # ["CSE", "IT", "ECE"]
    package_lpa = Column(Float, nullable=True)        # CTC in LPA
    location = Column(String)
    deadline = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    company = relationship("Company", back_populates="jobs")
    applications = relationship("Application", back_populates="job")
