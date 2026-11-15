import os
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
MODEL_PATH = os.path.join(os.path.dirname(__file__), "safelife_model.pkl")

# Variable globale pour conserver le modèle en mémoire
model = None

def generate_default_model():
    """Génère et sauvegarde un modèle RandomForest par défaut si le fichier .pkl n'existe pas."""
    print(" Génération d'un modèle IA initial...")
    
    # Données fictives d'entraînement [bpm, spo2, temperature, piezo, gsr, acceleration]
    X_train = np.array([
        [75, 98.0, 36.6, 0.2, 1.5, 0.1],  # Normal
        [80, 97.5, 36.8, 0.3, 1.2, 0.2],  # Normal
        [140, 88.0, 38.5, 2.5, 5.0, 3.5], # Crise
        [135, 85.0, 39.0, 3.0, 6.2, 4.0], # Crise
        [65, 99.0, 36.5, 0.1, 1.0, 0.0],  # Normal
        [150, 89.0, 37.2, 2.1, 4.8, 2.8]  # Crise
    ])
    y_train = np.array([0, 0, 1, 1, 0, 1])  # 0: Normal, 1: Crise

    clf = RandomForestClassifier(n_estimators=10, random_state=42)
    clf.fit(X_train, y_train)

    joblib.dump(clf, MODEL_PATH)
    print(f" Modèle créé et sauvegardé sous : {MODEL_PATH}")
    return clf

def load_model():
    """Charge le modèle au démarrage ou le génère s'il est introuvable."""
    global model
    if not os.path.exists(MODEL_PATH):
        model = generate_default_model()
    else:
        model = joblib.load(MODEL_PATH)
        print("Modèle IA chargé avec succès.")

def predire_crise(bpm: int, spo2: float, temperature: float, piezo: float, gsr: float, acceleration: float):
    """Effectue une prédiction à partir des données transmises."""
    if model is None:
        load_model()

    features = np.array([[bpm, spo2, temperature, piezo, gsr, acceleration]])
    prediction = int(model.predict(features)[0])
    probabilite = float(model.predict_proba(features)[0][1])
    
    return prediction, probabilite