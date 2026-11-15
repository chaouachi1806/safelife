from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base, SessionLocal
from .routers import donnees, patients, alertes, auth
from .services.ai_model import load_model
from .models import Medecin, Patient
from .routers.auth import hasher_password
from dotenv import load_dotenv
load_dotenv()
import os

Base.metadata.create_all(bind=engine)

def seed_default_users():
    db = SessionLocal()
    try:
        # Seed Médecin
        medecin = db.query(Medecin).filter(Medecin.email == "doctor@gmail.com").first()
        if not medecin:
            medecin = Medecin(
                nom="Doctor",
                prenom="SafeLife",
                email="doctor@gmail.com",
                password=hasher_password(os.getenv("DEMO_PASSWORD")),
                service="Cardiologie"
            )
            db.add(medecin)
            db.commit()
            db.refresh(medecin)
            print("✅ Médecin doctor@gmail.com créé!")

        # Seed Patient
        patient = db.query(Patient).filter(Patient.email == "patient@gmail.com").first()
        if not patient:
            default_patient = Patient(
                nom="Ben Ali",
                prenom="Ahmed",
                age=30,
                email="patient@gmail.com",
                telephone="12345678",
                password=hasher_password(os.getenv("DEMO_PASSWORD")),
                medecin_id=medecin.id
            )
            db.add(default_patient)
            db.commit()
            print("✅ Patient patient@gmail.com créé!")

    except Exception as e:
        print(f"⚠️ Erreur seed users: {e}")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_model()
    seed_default_users()
    yield

app = FastAPI(title="SafeLife API", version="1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,    prefix="/api/auth",     tags=["Auth"])
app.include_router(donnees.router, prefix="/api/donnees",  tags=["Données"])
app.include_router(patients.router,prefix="/api/patients", tags=["Patients"])
app.include_router(alertes.router, prefix="/api/alertes",  tags=["Alertes"])

@app.get("/")
def root():
    return {"message": "SafeLife API opérationnelle"}