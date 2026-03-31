from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.student import Student
from app.models.application import Application
from app.models.job import Job

router = APIRouter()

@router.get("/leaderboard")
def get_leaderboard(
    department: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Global student leaderboard by placement readiness score."""
    students = db.query(Student).all()
    result = []

    for s in students:
        user = s.user
        if not user:
            continue
        if department and s.department != department:
            continue

        # Calculate readiness score (0-100)
        cgpa_score = min((s.cgpa or 0) / 10 * 30, 30)  # 30 pts
        skills_score = min(len(s.skills or []) * 4, 30)  # 30 pts max
        cert_score = min(len(s.certifications or []) * 5, 15)  # 15 pts max
        app_count = len(s.applications or [])
        activity_score = min(app_count * 5, 15)  # 15 pts max
        placed_bonus = 10 if s.placement_status in ['placed', 'selected'] else 0

        readiness = round(cgpa_score + skills_score + cert_score + activity_score + placed_bonus, 1)

        result.append({
            "rank": 0,
            "student_id": s.id,
            "name": user.full_name,
            "department": s.department or "—",
            "cgpa": s.cgpa,
            "skills_count": len(s.skills or []),
            "applications_count": app_count,
            "placement_status": s.placement_status or "unplaced",
            "readiness_score": readiness,
        })

    # Sort by readiness descending
    result.sort(key=lambda x: x["readiness_score"], reverse=True)
    for i, r in enumerate(result):
        r["rank"] = i + 1

    return result


@router.get("/departments")
def get_departments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get distinct departments."""
    students = db.query(Student.department).distinct().all()
    return [s[0] for s in students if s[0]]
