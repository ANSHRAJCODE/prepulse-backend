from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.models.user import User
from app.models.student import Student
from app.models.job import Job, Company
from app.models.application import Application
from app.core.dependencies import get_current_admin
from typing import List

router = APIRouter()


@router.get("/dashboard")
def admin_dashboard(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    total_students = db.query(Student).count()
    placed_students = db.query(Student).filter(Student.placement_status == "placed").count()
    total_jobs = db.query(Job).filter(Job.is_active == True).count()
    total_applications = db.query(Application).count()
    total_companies = db.query(Company).count()

    # Applications by status
    status_counts = db.query(
        Application.status,
        func.count(Application.id).label("count")
    ).group_by(Application.status).all()

    # Department-wise stats
    dept_stats = db.query(
        Student.department,
        func.count(Student.id).label("total"),
        func.avg(Student.cgpa).label("avg_cgpa")
    ).group_by(Student.department).all()

    # Top jobs by applications
    top_jobs = db.query(
        Job.id,
        Job.title,
        func.count(Application.id).label("applications")
    ).join(Application, Job.id == Application.job_id)\
     .group_by(Job.id, Job.title)\
     .order_by(func.count(Application.id).desc())\
     .limit(5).all()

    # Placement rate
    placement_rate = round((placed_students / total_students * 100), 1) if total_students > 0 else 0

    return {
        "overview": {
            "total_students": total_students,
            "placed_students": placed_students,
            "placement_rate": placement_rate,
            "active_jobs": total_jobs,
            "total_applications": total_applications,
            "total_companies": total_companies,
        },
        "application_pipeline": [
            {"status": s.status, "count": s.count} for s in status_counts
        ],
        "department_stats": [
            {
                "department": d.department or "Unknown",
                "total": d.total,
                "avg_cgpa": round(d.avg_cgpa or 0, 2)
            } for d in dept_stats
        ],
        "top_jobs": [
            {"job_id": j.id, "title": j.title, "applications": j.applications}
            for j in top_jobs
        ]
    }


@router.get("/students")
def list_all_students(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    students = db.query(Student).all()
    result = []
    for s in students:
        result.append({
            "id": s.id,
            "name": s.user.full_name if s.user else "Unknown",
            "email": s.user.email if s.user else "",
            "roll_number": s.roll_number,
            "department": s.department,
            "cgpa": s.cgpa,
            "skills": s.skills,
            "placement_status": s.placement_status,
            "skills_count": len(s.skills or []),
        })
    return result


@router.get("/readiness-heatmap")
def readiness_heatmap(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Returns placement readiness data per department."""
    students = db.query(Student).all()
    jobs = db.query(Job).filter(Job.is_active == True).limit(5).all()

    heatmap = {}
    for student in students:
        dept = student.department or "Unknown"
        if dept not in heatmap:
            heatmap[dept] = {"total": 0, "ready": 0, "avg_cgpa": 0, "cgpa_sum": 0}
        heatmap[dept]["total"] += 1
        heatmap[dept]["cgpa_sum"] += student.cgpa or 0
        if (student.cgpa or 0) >= 6.5 and len(student.skills or []) >= 3:
            heatmap[dept]["ready"] += 1

    result = []
    for dept, data in heatmap.items():
        readiness = round((data["ready"] / data["total"] * 100), 1) if data["total"] > 0 else 0
        result.append({
            "department": dept,
            "total_students": data["total"],
            "placement_ready": data["ready"],
            "readiness_percentage": readiness,
            "avg_cgpa": round(data["cgpa_sum"] / data["total"], 2) if data["total"] > 0 else 0,
        })

    return sorted(result, key=lambda x: x["readiness_percentage"], reverse=True)
