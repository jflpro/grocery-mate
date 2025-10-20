from sqlalchemy import text
from app.database import engine

try:
    # Essaye de se connecter à la DB
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("✅ Connexion réussie :", result.scalar())
except Exception as e:
    print("❌ Erreur de connexion :", e)
