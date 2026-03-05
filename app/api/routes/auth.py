from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.models.student import Student
from app.models.job import Company
from app.schemas.schemas import UserCreate, UserLogin, Token, UserOut
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.dependencies import get_current_user

router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=201)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check existing email
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Auto-create profile based on role
    if user_data.role.value == "student":
        student = Student(user_id=user.id, skills=[], certifications=[], projects=[])
        db.add(student)
        db.commit()
    elif user_data.role.value == "company":
        company = Company(user_id=user.id, company_name=user_data.full_name)
        db.add(company)
        db.commit()

    return user


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account is deactivated")

    token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    return Token(
        access_token=token,
        token_type="bearer",
        role=user.role.value,
        user_id=user.id,
        full_name=user.full_name,
    )


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
