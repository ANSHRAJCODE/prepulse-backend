from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any
from datetime import datetime
from app.models.user import UserRole


# ─── Auth Schemas ────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: UserRole = UserRole.student


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    user_id: int
    full_name: str


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Student Schemas ──────────────────────────────────────────────────────────

class StudentProfileCreate(BaseModel):
    roll_number: Optional[str] = None
    department: Optional[str] = None
    batch_year: Optional[int] = None
    cgpa: Optional[float] = 0.0
    skills: Optional[List[str]] = []
    certifications: Optional[List[str]] = []
    projects: Optional[List[dict]] = []
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None


class StudentProfileUpdate(StudentProfileCreate):
    pass


class StudentOut(BaseModel):
    id: int
    user_id: int
    roll_number: Optional[str]
    department: Optional[str]
    batch_year: Optional[int]
    cgpa: float
    skills: List[str]
    certifications: List[str]
    projects: List[Any]
    linkedin_url: Optional[str]
    github_url: Optional[str]
    placement_status: str
    user: UserOut

    class Config:
        from_attributes = True


# ─── Job Schemas ──────────────────────────────────────────────────────────────

class JobCreate(BaseModel):
    title: str
    description: Optional[str] = None
    role_type: str = "full_time"
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    min_cgpa: float = 6.0
    allowed_branches: List[str] = []
    package_lpa: Optional[float] = None
    location: Optional[str] = None
    deadline: Optional[datetime] = None


class JobOut(BaseModel):
    id: int
    company_id: int
    company_name: Optional[str] = None
    title: str
    description: Optional[str]
    role_type: str
    required_skills: List[str]
    preferred_skills: List[str]
    min_cgpa: float
    allowed_branches: List[str]
    package_lpa: Optional[float]
    location: Optional[str]
    deadline: Optional[datetime]
    is_active: bool
    created_at: datetime

    @classmethod
    def from_orm_with_company(cls, job):
        data = {
            "id": job.id,
            "company_id": job.company_id,
            "company_name": job.company.company_name if job.company else None,
            "title": job.title,
            "description": job.description,
            "role_type": job.role_type,
            "required_skills": job.required_skills,
            "preferred_skills": job.preferred_skills,
            "min_cgpa": job.min_cgpa,
            "allowed_branches": job.allowed_branches,
            "package_lpa": job.package_lpa,
            "location": job.location,
            "deadline": job.deadline,
            "is_active": job.is_active,
            "created_at": job.created_at,
        }
        return cls(**data)

    class Config:
        from_attributes = True


# ─── Application Schemas ──────────────────────────────────────────────────────

class ApplicationCreate(BaseModel):
    job_id: int


class ApplicationStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None


class ApplicationOut(BaseModel):
    id: int
    student_id: int
    job_id: int
    status: str
    match_percentage: float
    missing_skills: List[str]
    ai_roadmap: Optional[Any]
    applied_at: datetime
    notes: Optional[str]

    class Config:
        from_attributes = True


# ─── AI Schemas ───────────────────────────────────────────────────────────────

class RoadmapRequest(BaseModel):
    student_id: int
    job_id: int


class RoadmapResponse(BaseModel):
    match_percentage: float
    missing_skills: List[str]
    roadmap: str
    steps: List[dict]


# ─── Match Engine Response ────────────────────────────────────────────────────

class MatchResult(BaseModel):
    match_percentage: float
    missing_skills: List[str]
    matched_skills: List[str]
    cgpa_eligible: bool
    branch_eligible: bool
    overall_eligible: bool
