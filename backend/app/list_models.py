import os
from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

print("=== Liste des modèles Gemini disponibles ===")

try:
    models = client.models.list()
    for m in models:
        print(m.name)
except Exception as e:
    print(f"Erreur : {e}")
