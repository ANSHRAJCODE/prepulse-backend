from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, students, jobs, applications, admin, ai
from app.db.database import engine, SessionLocal
from app.models import user, student, job, application
from app.models.user import User
from app.core.config import settings

# Create all tables
user.Base.metadata.create_all(bind=engine)
student.Base.metadata.create_all(bind=engine)
job.Base.metadata.create_all(bind=engine)
application.Base.metadata.create_all(bind=engine)

# Auto-seed if database is empty
def auto_seed():
    db = SessionLocal()
    try:
        count = db.query(User).count()
        if count == 0:
            print("Database empty - running seed...")
            import seed
            seed.seed()
            print("Seed complete!")
        else:
            print(f"Database already has {count} users, skipping seed.")
    except Exception as e:
        print(f"Auto-seed error: {e}")
    finally:
        db.close()

auto_seed()

app = FastAPI(
    title="PrepPulse AI",
    description="AI-Driven Campus Placement Decision Support System",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(students.router, prefix="/api/students", tags=["Students"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(applications.router, prefix="/api/applications", tags=["Applications"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI Roadmap"])


@app.get("/")
def root():
    return {"message": "PrepPulse AI Backend is running", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}