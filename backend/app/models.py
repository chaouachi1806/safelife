from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base

class Patient(Base):
    __tablename__ = "patients"

    id         = Column(Integer, primary_key=True, index=True)
    nom        = Column(String, nullable=False)
    prenom     = Column(String, nullable=False)
    age        = Column(Integer)
    email      = Column(String, unique=True)
    telephone  = Column(String)
    password   = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    medecin_id = Column(Integer, ForeignKey("medecins.id"))

    medecin = relationship("Medecin", back_populates="patients")
    donnees = relationship("DonneesVitales", back_populates="patient")
    alertes = relationship("Alerte", back_populates="patient")


class Medecin(Base):
    __tablename__ = "medecins"

    id        = Column(Integer, primary_key=True, index=True)
    nom       = Column(String, nullable=False)
    prenom    = Column(String, nullable=False)
    email     = Column(String, unique=True)
    telephone = Column(String)
    service   = Column(String)
    password  = Column(String, nullable=False)

    patients = relationship("Patient", back_populates="medecin")


class DonneesVitales(Base):
    __tablename__ = "donnees_vitales"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    
    bpm = Column(Integer, default=0)
    spo2 = Column(Integer, default=0)
    temperature = Column(Float, default=0.0)
    piezo = Column(Float, default=0.0)
    ecg_courbe = Column(Text, default="[]")
    gsr = Column(Float, default=0.0)
    acceleration = Column(Float, default=0.0)
    score = Column(Integer, default=0)  # Assurez-vous que cette ligne est présente
    alerte = Column(String, default="")
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    phase = Column(String, default="P")  
    patient = relationship("Patient", back_populates="donnees")


class Alerte(Base):
    __tablename__ = "alertes"

    id           = Column(Integer, primary_key=True, index=True)
    patient_id   = Column(Integer, ForeignKey("patients.id"))
    type_alerte  = Column(String)
    score_risque = Column(Integer)
    description  = Column(String)
    resolue      = Column(Boolean, default=False)
    timestamp    = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    patient = relationship("Patient", back_populates="alertes")




         



