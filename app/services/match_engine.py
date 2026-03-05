"""
PrepPulse AI - Match Engine
Weighted scoring: CGPA (30%) + Skill Match (70%)
"""
from typing import List, Optional
from app.models.student import Student
from app.models.job import Job


def normalize_skill(skill: str) -> str:
    """Normalize skill string for comparison."""
    return skill.lower().strip().replace("-", "").replace(" ", "")


def calculate_match(student: Student, job: Job) -> dict:
    """
    Core matching algorithm.
    Returns match_percentage, missing_skills, matched_skills, eligibility flags.
    """
    # ── Eligibility Gates ────────────────────────────────────────────────────
    cgpa_eligible = student.cgpa >= job.min_cgpa

    branch_eligible = True
    if job.allowed_branches:
        branch_eligible = student.department in job.allowed_branches

    # ── Skill Matching ───────────────────────────────────────────────────────
    student_skills_normalized = {normalize_skill(s): s for s in (student.skills or [])}
    required_skills = job.required_skills or []
    preferred_skills = job.preferred_skills or []

    matched_required = []
    missing_required = []
    for skill in required_skills:
        if normalize_skill(skill) in student_skills_normalized:
            matched_required.append(skill)
        else:
            missing_required.append(skill)

    matched_preferred = []
    for skill in preferred_skills:
        if normalize_skill(skill) in student_skills_normalized:
            matched_preferred.append(skill)

    # ── Scoring ──────────────────────────────────────────────────────────────
    # Required skills: 70% weight
    required_score = 0.0
    if required_skills:
        required_score = (len(matched_required) / len(required_skills)) * 70
    else:
        required_score = 70.0  # No requirements = full score

    # Preferred skills: 10% weight
    preferred_score = 0.0
    if preferred_skills:
        preferred_score = (len(matched_preferred) / len(preferred_skills)) * 10
    else:
        preferred_score = 10.0

    # CGPA: 20% weight (scaled: min_cgpa = 0, 10.0 = 100%)
    max_cgpa = 10.0
    cgpa_score = min((student.cgpa / max_cgpa) * 20, 20)

    total_score = required_score + preferred_score + cgpa_score

    # Apply gate penalties
    if not cgpa_eligible:
        total_score = min(total_score, 40.0)  # Hard cap if CGPA fails
    if not branch_eligible:
        total_score = 0.0  # Branch mismatch = ineligible

    overall_eligible = cgpa_eligible and branch_eligible and total_score >= 50.0

    return {
        "match_percentage": round(total_score, 1),
        "missing_skills": missing_required,
        "matched_skills": matched_required + matched_preferred,
        "cgpa_eligible": cgpa_eligible,
        "branch_eligible": branch_eligible,
        "overall_eligible": overall_eligible,
    }


def rank_students_for_job(students: List[Student], job: Job) -> List[dict]:
    """Rank all students for a given job opening."""
    from app.models.application import Application
    results = []
    for student in students:
        match = calculate_match(student, job)
        # Check if student has applied to this job
        application = None
        for app in student.applications:
            if app.job_id == job.id:
                application = app
                break
        results.append({
            "student_id": student.id,
            "student_name": student.user.full_name if student.user else "Unknown",
            "roll_number": student.roll_number,
            "department": student.department,
            "cgpa": student.cgpa,
            "application_id": application.id if application else None,
            "application_status": application.status if application else None,
            **match,
        })
    return sorted(results, key=lambda x: x["match_percentage"], reverse=True)
