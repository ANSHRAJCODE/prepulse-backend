from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.application import Application
from app.models.student import Student
from app.models.job import Job
from app.schemas.schemas import ApplicationCreate, ApplicationStatusUpdate, ApplicationOut
from app.core.dependencies import get_current_user, get_current_student
from app.services.match_engine import calculate_match
from app.models.user import User

router = APIRouter()


@router.post("/apply", response_model=ApplicationOut, status_code=201)
def apply_to_job(
    data: ApplicationCreate,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    job = db.query(Job).filter(Job.id == data.job_id, Job.is_active == True).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or closed")

    # Check duplicate
    existing = db.query(Application).filter(
        Application.student_id == student.id,
        Application.job_id == data.job_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already applied to this job")

    # Calculate match
    match = calculate_match(student, job)

    application = Application(
        student_id=student.id,
        job_id=data.job_id,
        match_percentage=match["match_percentage"],
        missing_skills=match["missing_skills"],
        status="applied"
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


@router.get("/my", response_model=List[ApplicationOut])
def get_my_applications(
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Profile not found")
    return db.query(Application).filter(Application.student_id == student.id).all()


@router.patch("/{application_id}/status")
def update_status(
    application_id: int,
    data: ApplicationStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role.value not in ["admin", "company"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    valid_statuses = ["applied", "shortlisted", "interview", "selected", "rejected", "placed"]
    if data.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Choose from: {valid_statuses}")

    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    app.status = data.status
    if data.notes:
        app.notes = data.notes

    # If placed, update student placement status
    if data.status == "placed":
        student = db.query(Student).filter(Student.id == app.student_id).first()
        if student:
            student.placement_status = "placed"

    db.commit()
    db.refresh(app)
    return app


@router.get("/job/{job_id}")
def get_applications_for_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role.value not in ["admin", "company"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    apps = db.query(Application).filter(Application.job_id == job_id)\
        .order_by(Application.match_percentage.desc()).all()
    return apps
