from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db

router = APIRouter()

# 1. GET : Récupérer toutes les alertes d'un patient
@router.get("/patient/{patient_id}", response_model=List[schemas.AlerteOut])
def get_alertes_patient(patient_id: int, db: Session = Depends(get_db)):
    return db.query(models.Alerte).filter(models.Alerte.patient_id == patient_id).order_by(models.Alerte.timestamp.desc()).all()

# 2. GET : Récupérer UNIQUEMENT les alertes non résolues (Active Alerts)
@router.get("/patient/{patient_id}/actives", response_model=List[schemas.AlerteOut])
def get_alertes_actives(patient_id: int, db: Session = Depends(get_db)):
    return db.query(models.Alerte).filter(
        models.Alerte.patient_id == patient_id,
        models.Alerte.resolue == False
    ).order_by(models.Alerte.timestamp.desc()).all()

# 3. PUT : Marquer une alerte comme "Résolue" (quand le médecin traite le problème)
@router.put("/{alerte_id}/resoudre", response_model=schemas.AlerteOut)
def resoudre_alerte(alerte_id: int, db: Session = Depends(get_db)):
    alerte = db.query(models.Alerte).filter(models.Alerte.id == alerte_id).first()
    if not alerte:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Alerte introuvable"
        )
    
    alerte.resolue = True
    db.commit()
    db.refresh(alerte)
    return alerte