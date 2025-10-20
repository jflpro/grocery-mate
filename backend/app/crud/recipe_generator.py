import json
import asyncio
from typing import List, Dict, Any, Optional

# Importation de httpx pour les requêtes HTTP asynchrones
import httpx 
from fastapi import HTTPException, status

# Importez vos modèles SQLAlchemy et Pydantic pour la structure
from .. import models, schemas 

# Configuration de l'API Gemini
API_KEY = "" # Clé laissée vide pour l'environnement Canvas
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent"

# --- Schéma de Réponse pour la Génération (doit correspondre à schemas.RecipeCreate) ---

RECIPE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "title": {"type": "STRING", "description": "Le titre concis de la recette."},
        "description": {"type": "STRING", "description": "Une brève description."},
        "instructions": {"type": "STRING", "description": "Les instructions de préparation étape par étape."},
        "prep_time": {"type": "INTEGER", "description": "Temps de préparation en minutes."},
        "cook_time": {"type": "INTEGER", "description": "Temps de cuisson en minutes."},
        "servings": {"type": "INTEGER", "description": "Nombre de portions."},
        "calories": {"type": "INTEGER", "description": "Calories estimées par portion."},
        "is_healthy": {"type": "BOOLEAN", "description": "Vrai si la recette est considérée comme saine."},
        "is_public": {"type": "BOOLEAN", "description": "Toujours False pour les recettes générées par l'utilisateur."},
        "required_ingredients": {
            "type": "ARRAY",
            "description": "Liste des ingrédients requis avec quantité et unité.",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "name": {"type": "STRING"},
                    "quantity": {"type": "NUMBER"},
                    "unit": {"type": "STRING"}
                }
            }
        }
    },
    "required": ["title", "instructions", "servings", "required_ingredients"],
    "propertyOrdering": ["title", "description", "instructions", "prep_time", "cook_time", "servings", "calories", "is_healthy", "is_public", "required_ingredients"]
}


# --- Fonction Principale de Génération ---

async def generate_recipe_from_ingredients(
    user_ingredients: List[models.Ingredient]
) -> Dict[str, Any]:
    """
    Appelle l'API Gemini pour générer une recette basée sur l'inventaire de l'utilisateur.
    """
    
    # Formatage de l'inventaire pour le prompt
    inventory_list = []
    for ing in user_ingredients:
        # Simplification de l'affichage de la date d'expiration pour le modèle
        expiry_info = f" (Expires: {ing.expiry_date})" if ing.expiry_date else ""
        inventory_list.append(f"- {ing.name} ({ing.quantity} {ing.unit}, Category: {ing.category}){expiry_info}")

    inventory_text = "\n".join(inventory_list)
    
    # Instruction pour le modèle
    system_prompt = (
        "You are an expert culinary assistant. Your task is to generate one complete and detailed recipe "
        "that uses as many of the provided ingredients as possible. The recipe MUST be returned in the "
        "required JSON schema format, including the full list of required ingredients (even those from the inventory). "
        "Ensure the instructions are easy to follow."
    )
    
    user_query = f"""
    Generate a creative and delicious recipe using the following ingredients from a user's inventory. 
    Prioritize a simple, weeknight-friendly meal.

    User Inventory:
    {inventory_text}

    If necessary, you may suggest adding 2-3 common staple ingredients (like salt, pepper, oil) not listed above.
    """

    # Construction du payload de l'API
    payload = {
        "contents": [{"parts": [{"text": user_query}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": RECIPE_SCHEMA,
        },
    }

    # Logique d'appel API avec Backoff utilisant httpx
    max_retries = 3
    delay = 1
    
    # Utilisation de httpx.AsyncClient pour les appels
    async with httpx.AsyncClient(timeout=30.0) as client:
        for attempt in range(max_retries):
            try:
                # Effectuer l'appel à l'API en utilisant httpx
                response = await client.post(
                    API_URL,
                    headers={'Content-Type': 'application/json', 'X-API-Key': API_KEY},
                    json=payload # httpx gère la sérialisation JSON
                )
                
                # httpx lève une exception pour les statuts 4xx/5xx
                response.raise_for_status() 
                
                result = response.json()
                
                # Extraction et parsing du JSON généré
                json_text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text')
                
                if json_text:
                    parsed_recipe = json.loads(json_text)
                    return parsed_recipe
                
                # Si le contenu est vide, on lève une exception pour forcer la nouvelle tentative (si possible)
                raise Exception("Generated content was empty or missing from API response.")

            except (httpx.RequestError, httpx.HTTPStatusError, json.JSONDecodeError) as e:
                # Gère les erreurs de connexion, de statut HTTP et de parsing JSON
                if attempt < max_retries - 1:
                    await asyncio.sleep(delay)
                    delay *= 2  # Exponential backoff
                else:
                    # Échec après toutes les tentatives
                    detail = f"Erreur de l'API de génération de recette : {type(e).__name__} - {str(e)}"
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail=detail
                    )
            except Exception as e:
                # Gère toutes les autres erreurs non-API spécifiques
                if attempt < max_retries - 1:
                    await asyncio.sleep(delay)
                    delay *= 2
                else:
                    detail = f"Erreur interne inattendue : {str(e)}"
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=detail
                    )

    # Note: Cet endroit ne devrait pas être atteint
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erreur interne de génération de recette.")
