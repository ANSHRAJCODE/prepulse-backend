"""
PrepPulse - Database Seeder
Run: python seed.py
10 companies, 12 jobs, 25 students (7 ECSC), realistic applications
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal, engine
from app.models import user, student, job, application
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.job import Company, Job
from app.models.application import Application
from app.services.match_engine import calculate_match
from datetime import datetime, timedelta

user.Base.metadata.create_all(bind=engine)
student.Base.metadata.create_all(bind=engine)
job.Base.metadata.create_all(bind=engine)
application.Base.metadata.create_all(bind=engine)

db = SessionLocal()

def clean():
    db.query(Application).delete()
    db.query(Job).delete()
    db.query(Company).delete()
    db.query(Student).delete()
    db.query(User).delete()
    db.commit()
    print("✓ Cleaned existing data")

def seed():
    clean()

    # ── Admin ─────────────────────────────────────────────────────────────────
    admin = User(email="admin@demo.com", hashed_password=get_password_hash("demo123"),
                 full_name="Dr. Placement Head", role=UserRole.admin)
    db.add(admin)
    db.commit()
    db.refresh(admin)
    print("✓ Admin: admin@demo.com / demo123")

    # ── 10 Companies ──────────────────────────────────────────────────────────
    company_data = [
        ("TechCorp India",         "tech@demo.com"),
        ("DataSystems Pvt Ltd",    "data@demo.com"),
        ("StartupXYZ",             "startup@demo.com"),
        ("Infosys",                "infosys@demo.com"),
        ("Wipro Technologies",     "wipro@demo.com"),
        ("Amazon India",           "amazon@demo.com"),
        ("Tata Consultancy Services", "tcs@demo.com"),
        ("Cognizant",              "cognizant@demo.com"),
        ("HCL Technologies",       "hcl@demo.com"),
        ("Zoho Corporation",       "zoho@demo.com"),
    ]
    companies = []
    for name, email in company_data:
        cu = User(email=email, hashed_password=get_password_hash("demo123"),
                  full_name=name, role=UserRole.company)
        db.add(cu); db.commit(); db.refresh(cu)
        co = Company(user_id=cu.id, company_name=name, industry="Technology",
                     website=f"https://{name.lower().replace(' ','').replace('.','')}.com")
        db.add(co); db.commit(); db.refresh(co)
        companies.append(co)
    print(f"✓ {len(companies)} Companies created")

    # ── 12 Jobs ───────────────────────────────────────────────────────────────
    jobs_data = [
        # TechCorp India
        {
            "title": "Software Engineer - Backend",
            "company_id": companies[0].id,
            "description": "Build scalable backend services for our cloud platform.",
            "required_skills": ["Python", "FastAPI", "SQL", "Docker"],
            "preferred_skills": ["AWS", "Redis", "Kubernetes"],
            "min_cgpa": 7.0,
            "allowed_branches": ["CSE", "IT", "AIDS", "ECSC"],
            "package_lpa": 12.0, "location": "Bangalore", "role_type": "full_time"
        },
        {
            "title": "Full Stack Developer",
            "company_id": companies[0].id,
            "description": "Build end-to-end web applications.",
            "required_skills": ["JavaScript", "React", "Node.js", "MongoDB"],
            "preferred_skills": ["TypeScript", "Docker", "AWS"],
            "min_cgpa": 6.5,
            "allowed_branches": ["CSE", "IT", "ECE", "ECSC"],
            "package_lpa": 10.0, "location": "Hyderabad", "role_type": "full_time"
        },
        # DataSystems
        {
            "title": "Data Science Intern",
            "company_id": companies[1].id,
            "description": "Work on real ML projects with production data.",
            "required_skills": ["Python", "Machine Learning", "SQL"],
            "preferred_skills": ["TensorFlow", "PyTorch", "Data Science"],
            "min_cgpa": 7.5,
            "allowed_branches": ["CSE", "IT", "AIDS", "AIML", "ECSC"],
            "package_lpa": 4.0, "location": "Chennai", "role_type": "internship"
        },
        {
            "title": "Java Backend Engineer",
            "company_id": companies[1].id,
            "description": "Enterprise Java with Spring Boot microservices.",
            "required_skills": ["Java", "Spring Boot", "SQL", "REST APIs"],
            "preferred_skills": ["Microservices", "Docker", "AWS"],
            "min_cgpa": 6.0,
            "allowed_branches": ["CSE", "IT", "ECE", "ECSC", "EEE"],
            "package_lpa": 9.0, "location": "Pune", "role_type": "full_time"
        },
        # StartupXYZ
        {
            "title": "Frontend Developer",
            "company_id": companies[2].id,
            "description": "Build beautiful responsive UIs.",
            "required_skills": ["JavaScript", "React", "HTML/CSS"],
            "preferred_skills": ["TypeScript", "Tailwind CSS"],
            "min_cgpa": 6.0,
            "allowed_branches": ["CSE", "IT", "ECSC"],
            "package_lpa": 7.0, "location": "Remote", "role_type": "full_time"
        },
        # Infosys
        {
            "title": "ML Engineer",
            "company_id": companies[3].id,
            "description": "Build and deploy ML models at scale.",
            "required_skills": ["Python", "Machine Learning", "TensorFlow", "SQL"],
            "preferred_skills": ["PyTorch", "AWS", "Docker"],
            "min_cgpa": 7.5,
            "allowed_branches": ["CSE", "IT", "AIDS", "AIML", "ECSC"],
            "package_lpa": 14.0, "location": "Bangalore", "role_type": "full_time"
        },
        # Wipro
        {
            "title": "Systems Engineer",
            "company_id": companies[4].id,
            "description": "Enterprise software development and maintenance.",
            "required_skills": ["Python", "SQL", "REST APIs"],
            "preferred_skills": ["Java", "Git", "Docker"],
            "min_cgpa": 6.0,
            "allowed_branches": ["CSE", "IT", "ECE", "ECSC", "EEE", "ME"],
            "package_lpa": 6.5, "location": "Chennai", "role_type": "full_time"
        },
        # Amazon
        {
            "title": "SDE-1 Backend",
            "company_id": companies[5].id,
            "description": "Work on Amazon backend services and distributed systems.",
            "required_skills": ["Java", "Python", "SQL", "REST APIs", "Docker"],
            "preferred_skills": ["AWS", "Microservices", "Spring Boot"],
            "min_cgpa": 7.0,
            "allowed_branches": ["CSE", "IT", "ECSC"],
            "package_lpa": 26.0, "location": "Hyderabad", "role_type": "full_time"
        },
        # TCS
        {
            "title": "Associate Software Engineer",
            "company_id": companies[6].id,
            "description": "Software development across enterprise projects.",
            "required_skills": ["Python", "SQL", "Git"],
            "preferred_skills": ["Java", "REST APIs", "HTML/CSS"],
            "min_cgpa": 6.0,
            "allowed_branches": ["CSE", "IT", "ECE", "ECSC", "EEE", "AIDS", "AIML"],
            "package_lpa": 7.0, "location": "Multiple Cities", "role_type": "full_time"
        },
        # Cognizant
        {
            "title": "Programmer Analyst",
            "company_id": companies[7].id,
            "description": "Develop and maintain software solutions for global clients.",
            "required_skills": ["Java", "SQL", "REST APIs"],
            "preferred_skills": ["Spring Boot", "Python", "Git"],
            "min_cgpa": 6.0,
            "allowed_branches": ["CSE", "IT", "ECE", "ECSC", "EEE"],
            "package_lpa": 7.5, "location": "Chennai", "role_type": "full_time"
        },
        # HCL
        {
            "title": "Graduate Engineer Trainee",
            "company_id": companies[8].id,
            "description": "Engineering trainee programme across software domains.",
            "required_skills": ["Python", "SQL", "C++"],
            "preferred_skills": ["Java", "REST APIs", "Git"],
            "min_cgpa": 5.5,
            "allowed_branches": ["CSE", "IT", "ECE", "ECSC", "EEE", "ME", "CE"],
            "package_lpa": 5.5, "location": "Noida", "role_type": "full_time"
        },
        # Zoho
        {
            "title": "Software Developer",
            "company_id": companies[9].id,
            "description": "Build products used by millions of businesses worldwide.",
            "required_skills": ["Java", "SQL", "Data Structures", "REST APIs"],
            "preferred_skills": ["Python", "JavaScript", "React"],
            "min_cgpa": 7.0,
            "allowed_branches": ["CSE", "IT", "ECSC", "AIDS"],
            "package_lpa": 10.0, "location": "Chennai", "role_type": "full_time"
        },
    ]

    job_objects = []
    for jd in jobs_data:
        j = Job(**jd, deadline=datetime.now() + timedelta(days=30), is_active=True)
        db.add(j); db.commit(); db.refresh(j)
        job_objects.append(j)
    print(f"✓ {len(job_objects)} Jobs created")

    # ── 25 Students ───────────────────────────────────────────────────────────
    students_data = [
        # ── CSE (6 students) ──────────────────────────────────────────────────
        {
            "email": "student@demo.com", "name": "Arjun Sharma",
            "roll": "21CSE001", "dept": "CSE", "cgpa": 8.7, "batch": 2025,
            "skills": ["Python", "React", "SQL", "JavaScript", "Git", "REST APIs"],
            "certs": ["AWS Cloud Practitioner"],
        },
        {
            "email": "priya@demo.com", "name": "Priya Patel",
            "roll": "21CSE002", "dept": "CSE", "cgpa": 9.1, "batch": 2025,
            "skills": ["Python", "Machine Learning", "SQL", "Data Science", "TensorFlow"],
            "certs": ["Google Data Analytics"],
        },
        {
            "email": "ananya@demo.com", "name": "Ananya Iyer",
            "roll": "21CSE003", "dept": "CSE", "cgpa": 9.4, "batch": 2025,
            "skills": ["Python", "Django", "React", "PostgreSQL", "Docker", "AWS", "Git"],
            "certs": ["AWS Solutions Architect", "Docker Certified"],
        },
        {
            "email": "aditya@demo.com", "name": "Aditya Verma",
            "roll": "21CSE004", "dept": "CSE", "cgpa": 6.5, "batch": 2025,
            "skills": ["Java", "C++", "SQL", "Git"],
            "certs": [],
        },
        {
            "email": "nikhil@demo.com", "name": "Nikhil Joshi",
            "roll": "21CSE005", "dept": "CSE", "cgpa": 7.1, "batch": 2025,
            "skills": ["Python", "FastAPI", "SQL", "Git", "Docker"],
            "certs": [],
        },
        {
            "email": "siddharth@demo.com", "name": "Siddharth Rao",
            "roll": "21CSE006", "dept": "CSE", "cgpa": 9.0, "batch": 2025,
            "skills": ["Java", "Spring Boot", "Microservices", "Docker", "AWS", "SQL", "REST APIs"],
            "certs": ["AWS Developer Associate"],
        },
        # ── IT (4 students) ───────────────────────────────────────────────────
        {
            "email": "rahul@demo.com", "name": "Rahul Kumar",
            "roll": "21IT001", "dept": "IT", "cgpa": 7.2, "batch": 2025,
            "skills": ["Java", "Spring Boot", "SQL", "REST APIs"],
            "certs": [],
        },
        {
            "email": "rohan@demo.com", "name": "Rohan Mehta",
            "roll": "21IT002", "dept": "IT", "cgpa": 7.8, "batch": 2025,
            "skills": ["JavaScript", "React", "Node.js", "MongoDB", "HTML/CSS"],
            "certs": ["Meta Frontend Developer"],
        },
        {
            "email": "karan@demo.com", "name": "Karan Gupta",
            "roll": "21IT003", "dept": "IT", "cgpa": 8.2, "batch": 2025,
            "skills": ["React", "TypeScript", "Node.js", "MongoDB", "Docker"],
            "certs": [],
        },
        {
            "email": "tanvi@demo.com", "name": "Tanvi Shah",
            "roll": "21IT004", "dept": "IT", "cgpa": 7.5, "batch": 2025,
            "skills": ["Python", "SQL", "REST APIs", "Git", "JavaScript"],
            "certs": [],
        },
        # ── AIDS (3 students) ─────────────────────────────────────────────────
        {
            "email": "sneha@demo.com", "name": "Sneha Reddy",
            "roll": "21AIDS001", "dept": "AIDS", "cgpa": 8.0, "batch": 2025,
            "skills": ["Python", "SQL", "Machine Learning"],
            "certs": [],
        },
        {
            "email": "divya@demo.com", "name": "Divya Sharma",
            "roll": "21AIDS002", "dept": "AIDS", "cgpa": 8.8, "batch": 2025,
            "skills": ["Python", "Machine Learning", "Data Science", "SQL", "TensorFlow", "PyTorch"],
            "certs": ["Coursera ML Specialization"],
        },
        {
            "email": "aryan@demo.com", "name": "Aryan Kapoor",
            "roll": "21AIDS003", "dept": "AIDS", "cgpa": 7.6, "batch": 2025,
            "skills": ["Python", "SQL", "Data Science", "Machine Learning"],
            "certs": [],
        },
        # ── AIML (2 students) ─────────────────────────────────────────────────
        {
            "email": "kavya@demo.com", "name": "Kavya Nair",
            "roll": "21AIML001", "dept": "AIML", "cgpa": 8.5, "batch": 2025,
            "skills": ["Python", "Machine Learning", "Data Science", "TensorFlow", "SQL"],
            "certs": ["DeepLearning.AI TensorFlow"],
        },
        {
            "email": "ishaan@demo.com", "name": "Ishaan Trivedi",
            "roll": "21AIML002", "dept": "AIML", "cgpa": 8.0, "batch": 2025,
            "skills": ["Python", "PyTorch", "Machine Learning", "SQL"],
            "certs": [],
        },
        # ── ECSC (7 students) — your branch, heavy representation ─────────────
        {
            "email": "ansh@demo.com", "name": "Ansh Raj",
            "roll": "21ECSC001", "dept": "ECSC", "cgpa": 8.2, "batch": 2025,
            "skills": ["Python", "C++", "SQL", "REST APIs", "Git"],
            "certs": [],
        },
        {
            "email": "vikram@demo.com", "name": "Vikram Singh",
            "roll": "21ECSC002", "dept": "ECSC", "cgpa": 6.8, "batch": 2025,
            "skills": ["C", "C++", "Python", "SQL"],
            "certs": [],
        },
        {
            "email": "meera@demo.com", "name": "Meera Krishnan",
            "roll": "21ECSC003", "dept": "ECSC", "cgpa": 7.9, "batch": 2025,
            "skills": ["Python", "Java", "REST APIs", "SQL", "Git"],
            "certs": [],
        },
        {
            "email": "rohit@demo.com", "name": "Rohit Nair",
            "roll": "21ECSC004", "dept": "ECSC", "cgpa": 7.4, "batch": 2025,
            "skills": ["Python", "C++", "SQL", "Docker", "Git"],
            "certs": [],
        },
        {
            "email": "shreya@demo.com", "name": "Shreya Bose",
            "roll": "21ECSC005", "dept": "ECSC", "cgpa": 8.6, "batch": 2025,
            "skills": ["Java", "Spring Boot", "SQL", "REST APIs", "Python", "Docker"],
            "certs": ["Oracle Java SE Certified"],
        },
        {
            "email": "aman@demo.com", "name": "Aman Tiwari",
            "roll": "21ECSC006", "dept": "ECSC", "cgpa": 6.2, "batch": 2025,
            "skills": ["C", "Python", "SQL"],
            "certs": [],
        },
        {
            "email": "nisha@demo.com", "name": "Nisha Pandey",
            "roll": "21ECSC007", "dept": "ECSC", "cgpa": 7.1, "batch": 2025,
            "skills": ["Python", "JavaScript", "HTML/CSS", "SQL", "Git"],
            "certs": [],
        },
        # ── EEE (2 students) ──────────────────────────────────────────────────
        {
            "email": "pooja@demo.com", "name": "Pooja Desai",
            "roll": "21EEE001", "dept": "EEE", "cgpa": 6.9, "batch": 2025,
            "skills": ["Python", "MATLAB", "C", "SQL"],
            "certs": [],
        },
        {
            "email": "suresh@demo.com", "name": "Suresh Babu",
            "roll": "21EEE002", "dept": "EEE", "cgpa": 6.3, "batch": 2025,
            "skills": ["C", "Python", "MATLAB"],
            "certs": [],
        },
        # ── ME (1 student) ────────────────────────────────────────────────────
        {
            "email": "deepak@demo.com", "name": "Deepak Mishra",
            "roll": "21ME001", "dept": "ME", "cgpa": 6.1, "batch": 2025,
            "skills": ["Python", "C", "SQL"],
            "certs": [],
        },
    ]

    student_objects = []
    for sd in students_data:
        su = User(email=sd["email"], hashed_password=get_password_hash("demo123"),
                  full_name=sd["name"], role=UserRole.student)
        db.add(su); db.commit(); db.refresh(su)
        st = Student(user_id=su.id, roll_number=sd["roll"], department=sd["dept"],
                     batch_year=sd["batch"], cgpa=sd["cgpa"], skills=sd["skills"],
                     certifications=sd.get("certs", []), projects=[])
        db.add(st); db.commit(); db.refresh(st)
        student_objects.append(st)
    print(f"✓ {len(student_objects)} Students created")

    # ── Applications ──────────────────────────────────────────────────────────
    def apply(student, job_obj, status="applied"):
        match = calculate_match(student, job_obj)
        db.add(Application(
            student_id=student.id, job_id=job_obj.id,
            match_percentage=match["match_percentage"],
            missing_skills=match["missing_skills"], status=status
        ))

    # Shortcuts
    arjun    = student_objects[0]
    priya    = student_objects[1]
    ananya   = student_objects[2]
    aditya   = student_objects[3]
    siddharth= student_objects[5]
    rahul    = student_objects[6]
    rohan    = student_objects[7]
    karan    = student_objects[8]
    tanvi    = student_objects[9]
    sneha    = student_objects[10]
    divya    = student_objects[11]
    aryan    = student_objects[12]
    kavya    = student_objects[13]
    ishaan   = student_objects[14]
    ansh     = student_objects[15]   # ECSC
    vikram   = student_objects[16]   # ECSC
    meera    = student_objects[17]   # ECSC
    rohit    = student_objects[18]   # ECSC
    shreya   = student_objects[19]   # ECSC
    aman     = student_objects[20]   # ECSC
    nisha    = student_objects[21]   # ECSC
    pooja    = student_objects[22]
    suresh   = student_objects[23]
    deepak   = student_objects[24]

    # CSE students
    apply(arjun,     job_objects[0],  "applied")
    apply(arjun,     job_objects[1],  "shortlisted")
    apply(arjun,     job_objects[8],  "applied")
    apply(priya,     job_objects[2],  "shortlisted")
    apply(priya,     job_objects[5],  "applied")
    apply(ananya,    job_objects[0],  "interview")
    apply(ananya,    job_objects[7],  "applied")
    apply(aditya,    job_objects[8],  "applied")
    apply(aditya,    job_objects[10], "applied")
    apply(siddharth, job_objects[3],  "shortlisted")
    apply(siddharth, job_objects[7],  "interview")
    apply(siddharth, job_objects[11], "applied")

    # IT students
    apply(rahul,  job_objects[3],  "applied")
    apply(rahul,  job_objects[9],  "applied")
    apply(rohan,  job_objects[1],  "applied")
    apply(rohan,  job_objects[4],  "shortlisted")
    apply(karan,  job_objects[4],  "applied")
    apply(karan,  job_objects[1],  "shortlisted")
    apply(tanvi,  job_objects[8],  "applied")
    apply(tanvi,  job_objects[6],  "applied")

    # AIDS / AIML
    apply(sneha,  job_objects[2],  "applied")
    apply(divya,  job_objects[2],  "shortlisted")
    apply(divya,  job_objects[5],  "applied")
    apply(aryan,  job_objects[2],  "applied")
    apply(aryan,  job_objects[8],  "applied")
    apply(kavya,  job_objects[2],  "shortlisted")
    apply(kavya,  job_objects[5],  "applied")
    apply(ishaan, job_objects[5],  "applied")
    apply(ishaan, job_objects[2],  "applied")

    # ECSC students — applying to all eligible jobs
    apply(ansh,   job_objects[0],  "applied")      # Software Engineer Backend
    apply(ansh,   job_objects[6],  "applied")      # Systems Engineer (Wipro)
    apply(ansh,   job_objects[8],  "applied")      # TCS Associate
    apply(vikram, job_objects[3],  "applied")      # Java Backend
    apply(vikram, job_objects[6],  "applied")      # Systems Engineer
    apply(vikram, job_objects[10], "applied")      # HCL GET
    apply(meera,  job_objects[1],  "applied")      # Full Stack
    apply(meera,  job_objects[6],  "shortlisted")  # Systems Engineer
    apply(meera,  job_objects[9],  "applied")      # Cognizant
    apply(rohit,  job_objects[0],  "applied")      # Software Engineer
    apply(rohit,  job_objects[6],  "applied")      # Wipro
    apply(rohit,  job_objects[10], "applied")      # HCL
    apply(shreya, job_objects[3],  "shortlisted")  # Java Backend
    apply(shreya, job_objects[7],  "applied")      # Amazon SDE-1
    apply(shreya, job_objects[11], "applied")      # Zoho
    apply(aman,   job_objects[6],  "applied")      # Wipro
    apply(aman,   job_objects[10], "applied")      # HCL GET
    apply(nisha,  job_objects[4],  "applied")      # Frontend
    apply(nisha,  job_objects[8],  "applied")      # TCS

    # EEE / ME
    apply(pooja,  job_objects[6],  "applied")
    apply(pooja,  job_objects[10], "applied")
    apply(suresh, job_objects[10], "applied")
    apply(deepak, job_objects[10], "applied")

    db.commit()
    print("✓ Sample applications created")

    print("\n" + "="*60)
    print("  PrepPulse — Database Seeded Successfully")
    print("="*60)
    print("\n  Demo Accounts (all passwords: demo123)")
    print("  ────────────────────────────────────────────")
    print("  Admin     : admin@demo.com")
    print("  ────────────────────────────────────────────")
    print("  Companies : tech@demo.com         TechCorp India")
    print("              amazon@demo.com        Amazon India")
    print("              infosys@demo.com       Infosys")
    print("              tcs@demo.com           TCS")
    print("              zoho@demo.com          Zoho")
    print("              + 5 more companies")
    print("  ────────────────────────────────────────────")
    print("  ECSC      : ansh@demo.com          Ansh Raj (8.2)")
    print("              shreya@demo.com        Shreya Bose (8.6)")
    print("              meera@demo.com         Meera Krishnan (7.9)")
    print("              rohit@demo.com         Rohit Nair (7.4)")
    print("              vikram@demo.com        Vikram Singh (6.8)")
    print("              aman@demo.com          Aman Tiwari (6.2)")
    print("              nisha@demo.com         Nisha Pandey (7.1)")
    print("  ────────────────────────────────────────────")
    print("  Others    : student@demo.com       Arjun (CSE)")
    print("              priya@demo.com         Priya (CSE)")
    print("              kavya@demo.com         Kavya (AIML)")
    print("              + 11 more students")
    print("="*60)

if __name__ == "__main__":
    seed()
    db.close()
