import os
import bcrypt
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional

from ..database import get_db
from .. import models

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY manquante : définis-la dans .env")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def hasher_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

def verifier_password(password: str, hashed: str) -> bool:
    pwd_bytes = password.encode('utf-8')[:72]
    hashed_bytes = hashed.encode('utf-8')
    return bcrypt.checkpw(pwd_bytes, hashed_bytes)

def creer_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou expiré",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        role: str  = payload.get("role")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    if role == "medecin":
        user = db.query(models.Medecin).filter(models.Medecin.email == email).first()
    else:
        user = db.query(models.Patient).filter(models.Patient.email == email).first()

    if user is None:
        raise credentials_exception

    user.role = role
    return user

class UserCreate(BaseModel):
    nom: str
    prenom: str
    email: EmailStr
    password: str
    role: str

class LoginSchema(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: str

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    hashed_pwd = hasher_password(user_data.password)

    if user_data.role == "medecin":
        if db.query(models.Medecin).filter(models.Medecin.email == user_data.email).first():
            raise HTTPException(status_code=400, detail="Email déjà utilisé")
        
        nouveau_user = models.Medecin(
            nom=user_data.nom,
            prenom=user_data.prenom,
            email=user_data.email,
            password=hashed_pwd
        )
    else:
        if db.query(models.Patient).filter(models.Patient.email == user_data.email).first():
            raise HTTPException(status_code=400, detail="Email déjà utilisé")

        nouveau_user = models.Patient(
            nom=user_data.nom,
            prenom=user_data.prenom,
            email=user_data.email,
            password=hashed_pwd
        )

    db.add(nouveau_user)
    db.commit()
    db.refresh(nouveau_user)
    return {"message": f"Compte {user_data.role} créé avec succès !"}

# Route de Connexion hybride (Supporte JSON Frontend & Form Data Swagger)
@router.post("/login")
async def login(request: Request, db: Session = Depends(get_db)):
    email_or_user = None
    password = None

    # Extraction des données (JSON ou Form Data)
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        data = await request.json()
        email_or_user = data.get("email") or data.get("username")
        password = data.get("password")
    else:
        form_data = await request.form()
        email_or_user = form_data.get("username") or form_data.get("email")
        password = form_data.get("password")

    if not email_or_user or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email/Username et mot de passe requis."
        )

    # 1. Recherche dans les Médecins
    user = db.query(models.Medecin).filter(models.Medecin.email == email_or_user).first()
    role = "medecin"

    # 2. Si non trouvé, recherche dans les Patients
    if not user:
        user = db.query(models.Patient).filter(models.Patient.email == email_or_user).first()
        role = "patient"

    if not user or not verifier_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )

    access_token = creer_token(data={"sub": user.email, "role": role})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": role,
        "email": user.email,
        "nom": user.nom,
        "prenom": user.prenom
    }

@router.get("/me")
def read_users_me(current_user=Depends(get_current_user)):
    return current_user