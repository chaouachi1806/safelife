import sqlite3
import bcrypt
import os
from dotenv import load_dotenv
load_dotenv()


conn = sqlite3.connect('safelife.db')
cursor = conn.cursor()


hashed_password = bcrypt.hashpw(os.getenv("DEMO_PASSWORD").encode(), bcrypt.gensalt()).decode('utf-8')

cursor.execute("SELECT email FROM patients WHERE email = ?", ("patient@gmail.com",))
user = cursor.fetchone()

if user:
    cursor.execute("UPDATE patients SET password = ? WHERE email = ?", (hashed_password, "patient@gmail.com"))
    print(" Mot de passe mis à jour ! (Email: patient@gmail.com)")
else:
    cursor.execute(
        "INSERT INTO patients (nom, prenom, email, password) VALUES (?, ?, ?, ?)",
        ("Patient", "SafeLife", "patient@gmail.com", hashed_password)
    )
    print("Nouveau patient créé ! (Email: patient@gmail.com )")

conn.commit()
conn.close()