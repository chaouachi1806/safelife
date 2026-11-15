from datetime import datetime, timezone
from app.database import SessionLocal, engine, Base
from app import models
from app.routers.auth import hasher_password
import os

# 1. Re-créer proprement les tables
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()

print("" \
" Réinitialisation de la base de données...")

# 2. Créer le Médecin
medecin = models.Medecin(
    nom="Ben Amor",
    prenom="Mohamed",
    email="doctor@gmail.com",
    password=hasher_password(os.getenv("DEMO_PASSWORD"))
)
db.add(medecin)
db.commit()
db.refresh(medecin)


patient = models.Patient(
    nom="Chaouachi",
    prenom="Amel",
    email="patient@gmail.com",
    password=hasher_password(os.getenv("DEMO_PASSWORD")),
    age=45,
    medecin_id=medecin.id
)
db.add(patient)
db.commit()
db.refresh(patient)  


donnee = models.DonneesVitales(
    patient_id=patient.id, 
    spo2=99,
    temperature=36.9,
    piezo=14.2,
    ecg_courbe="[0.12, 0.15, 0.85, -0.4, 0.02, 0.1, 0.15, 0.9, -0.35]",
    gsr=310.5,
    acceleration=0.98,
    score=92,
    alerte="Aucune",
    timestamp=datetime.now(timezone.utc)
)
db.add(donnee)
db.commit()

print(f" Base initialisée ! Patient ID généré : {patient.id}")
db.close()