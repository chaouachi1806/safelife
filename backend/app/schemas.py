from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DonneesVitalesCreate(BaseModel):
    patient_id   : Optional[int] = None
    bpm          : int
    spo2         : float
    temperature  : float
    piezo        : Optional[float] = 0.0
    ecg_courbe   : Optional[str] = "[]"
    gsr          : Optional[float] = 0.0
    acceleration : Optional[float] = 0.0
    score        : Optional[float] = 0.0
    alerte       : Optional[str] = ""
    phase        : Optional[str] = "P"

class DonneesVitalesOut(BaseModel):
    id          : int
    patient_id  : Optional[int] = None
    bpm         : int
    spo2        : float
    temperature : float
    phase       : Optional[str] = "P"
    score       : Optional[float] = 0.0
    alerte      : Optional[str] = "Normal"
    prediction_crise : Optional[bool] = False 
    timestamp   : datetime

    class Config:
        from_attributes = True

# 1. Schéma pour la CRÉATION d'une alerte
class AlerteCreate(BaseModel):
    patient_id: int
    type_alerte: str
    score_risque: int
    description: str
    resolue: bool = False        

class AlerteOut(BaseModel):
    id           : int
    patient_id   : int
    type_alerte  : str
    score_risque : int
    resolue      : bool
    timestamp    : datetime

    class Config:
        from_attributes = True