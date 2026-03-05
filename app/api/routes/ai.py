from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.student import Student
from app.models.job import Job, Company
from app.models.application import Application
from app.services.ollama_service import generate_roadmap
from app.services.match_engine import calculate_match
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/roadmap/{job_id}")
async def get_ai_roadmap(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate AI-powered learning roadmap for a student-job pair."""
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    company = db.query(Company).filter(Company.id == job.company_id).first()
    company_name = company.company_name if company else "Target Company"

    # Get match analysis
    match = calculate_match(student, job)

    # Generate AI roadmap
    roadmap = await generate_roadmap(
        student_name=current_user.full_name,
        department=student.department or "Engineering",
        cgpa=student.cgpa or 0.0,
        current_skills=student.skills or [],
        missing_skills=match["missing_skills"],
        job_title=job.title,
        company_name=company_name,
        required_skills=job.required_skills or [],
        preferred_skills=job.preferred_skills or [],
        role_type=job.role_type,
        match_percentage=match["match_percentage"],
    )

    # Cache in application if exists
    application = db.query(Application).filter(
        Application.student_id == student.id,
        Application.job_id == job_id
    ).first()
    if application:
        application.ai_roadmap = roadmap
        db.commit()

    return {
        "match_analysis": match,
        "roadmap": roadmap,
        "job": {
            "id": job.id,
            "title": job.title,
            "company": company_name,
        }
    }


@router.get("/status")
async def ollama_status():
    """Check if Ollama is running."""
    import httpx
    from app.core.config import settings
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            data = resp.json()
            models = [m["name"] for m in data.get("models", [])]
            return {"status": "online", "models": models}
    except Exception:
        return {"status": "offline", "message": "Ollama not running. Fallback mode active."}
