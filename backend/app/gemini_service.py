import os
import time
import google.generativeai as genai

# --- Configuration du client Gemini ---
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY manquant dans l'environnement du backend.")

genai.configure(api_key=API_KEY)

def ask_gemini(prompt: str) -> str:
    """
    Envoie un prompt à Google Gemini et renvoie la réponse textuelle.
    Gère les erreurs temporaires (503) avec plusieurs tentatives.
    """
    models_to_try = [
        "models/gemini-2.0-flash",
        "models/gemini-2.0-pro",
    ]

    for model in models_to_try:
        for attempt in range(3):
            try:
                response = genai.GenerativeModel(model).generate_content(prompt)
                if hasattr(response, "text"):
                    return response.text.strip()
                elif hasattr(response, "candidates"):
                    return response.candidates[0].content.parts[0].text
                else:
                    return str(response)
            except Exception as e:
                err = str(e)
                if "503" in err or "UNAVAILABLE" in err:
                    print(f"[!] Modèle {model} surchargé — tentative {attempt + 1}/3...")
                    time.sleep(2)
                    continue
                else:
                    return f"Erreur lors de l'appel à Gemini ({model}) : {e}"

    return "Erreur : tous les modèles Gemini sont temporairement indisponibles."
