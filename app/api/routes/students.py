from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.student import Student
from app.models.user import User
from app.schemas.schemas import StudentProfileCreate, StudentProfileUpdate, StudentOut
from app.core.dependencies import get_current_user, get_current_student

router = APIRouter()


@router.get("/profile", response_model=StudentOut)
def get_my_profile(
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return student


@router.put("/profile", response_model=StudentOut)
def update_profile(
    data: StudentProfileUpdate,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(student, key, value)

    db.commit()
    db.refresh(student)
    return student


@router.get("/{student_id}", response_model=StudentOut)
def get_student_by_id(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student
