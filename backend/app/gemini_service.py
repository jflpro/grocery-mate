import os
import time
import google.generativeai as genai

# --- Gemini client configuration ---
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing in the backend environment.")

genai.configure(api_key=API_KEY)


def ask_gemini(prompt: str) -> str:
    """
    Send a prompt to Google Gemini and return the textual response.
    Handles temporary errors (e.g. 503 / UNAVAILABLE) with multiple retry attempts.
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
                    print(f"[!] Model {model} overloaded — attempt {attempt + 1}/3...")
                    time.sleep(2)
                    continue
                else:
                    return f"Error while calling Gemini ({model}): {e}"

    return "Error: all Gemini models are temporarily unavailable."
