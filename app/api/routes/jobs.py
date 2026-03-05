from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models.job import Job, Company
from app.models.student import Student
from app.schemas.schemas import JobCreate, JobOut
from app.core.dependencies import get_current_user, get_current_company
from app.services.match_engine import calculate_match, rank_students_for_job
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=List[JobOut])
def list_jobs(
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Job)
    if active_only:
        query = query.filter(Job.is_active == True)
    # Companies only see their own job postings
    if current_user.role.value == "company":
        company = db.query(Company).filter(Company.user_id == current_user.id).first()
        if company:
            query = query.filter(Job.company_id == company.id)
    return query.all()


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/", response_model=JobOut, status_code=201)
def create_job(
    job_data: JobCreate,
    current_user: User = Depends(get_current_company),
    db: Session = Depends(get_db)
):
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company profile not found")

    job = Job(**job_data.dict(), company_id=company.id)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.get("/{job_id}/match")
def get_my_match(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get match percentage for current student vs a job."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    return calculate_match(student, job)


@router.get("/{job_id}/ranked-students")
def get_ranked_students(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin/Company: Get all students ranked for this job."""
    if current_user.role.value not in ["admin", "company"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    students = db.query(Student).all()
    return rank_students_for_job(students, job)
