from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.DonneesVitalesOut)
def ajouter_donnee(donnee: schemas.DonneesVitalesCreate, db: Session = Depends(get_db)):
    try:
        # 1. Verification Patient
        patient = None
        if donnee.patient_id:
            patient = db.query(models.Patient).filter(models.Patient.id == donnee.patient_id).first()
        
        if not patient:
            patient = db.query(models.Patient).first()
            if not patient:
                raise HTTPException(status_code=404, detail="Aucun patient trouvé")

        p_id = patient.id
        bpm_val = int(donnee.bpm)
        spo2_val = float(donnee.spo2)
        temp_val = float(donnee.temperature)

        # 2. Moteur d'Analyse / IA Score
        score_calcule = 0.0
        alertes_generees = []

        if bpm_val > 100 or bpm_val < 50:
            type_bpm = "Tachycardie" if bpm_val > 100 else "Bradycardie"
            alertes_generees.append(f"{type_bpm} ({bpm_val} BPM)")
            score_calcule += 40.0

        if spo2_val < 92 and spo2_val > 0:
            alertes_generees.append(f"Hypoxémie ({spo2_val}%)")
            score_calcule += 50.0

        if temp_val > 38.5:
            alertes_generees.append(f"Fièvre ({temp_val}°C)")
            score_calcule += 30.0

        score_final = min(score_calcule, 100.0)
        est_crise = len(alertes_generees) > 0  # <--- HĀDHA AL-BOOLEAN EL-MOHIM
        
        if est_crise:
            libelle_alerte = "CRITIQUE : " + ", ".join(alertes_generees)
            phase_val = "CRITIQUE"
        else:
            libelle_alerte = "Normal"
            phase_val = "Normal"

        # 3. Sauvegarde
        donnee_dict = donnee.dict()
        donnee_dict["patient_id"] = p_id
        donnee_dict["bpm"] = bpm_val
        donnee_dict["spo2"] = spo2_val
        donnee_dict["temperature"] = temp_val
        donnee_dict["score"] = score_final
        donnee_dict["alerte"] = libelle_alerte
        donnee_dict["phase"] = phase_val

        nouvelle_donnee = models.DonneesVitales(**donnee_dict)
        db.add(nouvelle_donnee)
        db.commit()
        db.refresh(nouvelle_donnee)

        # 4. Création Alertes fi Table Alerte
        if alertes_generees:
            for alt_desc in alertes_generees:
                nouvelle_alerte = models.Alerte(
                    patient_id=p_id,
                    type_alerte="Urgence Vitale",
                    score_risque=int(score_final),
                    description=alt_desc,
                    resolue=False
                )
                db.add(nouvelle_alerte)
            db.commit()

        # Injecter prediction_crise pour la réponse JSON Pydantic/React
        setattr(nouvelle_donnee, "prediction_crise", est_crise)

        return nouvelle_donnee

    except Exception as e:
        print(f"⚠️ Erreur insertion données: {e}")
        raise HTTPException(status_code=500, detail=str(e))