from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Patient

router = APIRouter()

@router.get("/")
def liste_patients(db: Session = Depends(get_db)):
    return db.query(Patient).all()

@router.get("/{patient_id}")
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    return db.query(Patient).filter(Patient.id == patient_id).first()