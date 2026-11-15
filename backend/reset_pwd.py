import sqlite3
import bcrypt
import os
from dotenv import load_dotenv
load_dotenv()


conn = sqlite3.connect('safelife.db')
cursor = conn.cursor()


hashed_password = bcrypt.hashpw(os.getenv("DEMO_PASSWORD").encode(), bcrypt.gensalt()).decode('utf-8')


cursor.execute("UPDATE medecins SET password = ? WHERE email = ?", (hashed_password, "doctor@gmail.com"))
conn.commit()

if cursor.rowcount > 0:
    print("Mot de passe mis à jour avec succès pour doctor@gmail.com !")
else:
    print("Aucun médecin trouvé avec cet email.")

conn.close()