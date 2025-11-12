from fastapi import APIRouter, Query, HTTPException
from app.gemini_service import ask_gemini

# ✅ Routeur sans préfixe local — le préfixe /api/ai est ajouté dans main.py
router = APIRouter(tags=["AI"])

@router.get("/recipe")
def generate_recipe(
    ingredients: str = Query(..., description="Liste d'ingrédients séparés par des virgules")
):
    """
    Génère une recette simple à partir d'une liste d'ingrédients.
    Exemple : /api/ai/recipe?ingredients=poulet,carottes,riz
    """
    prompt = f"Génère une recette simple et appétissante avec ces ingrédients : {ingredients}"

    try:
        result = ask_gemini(prompt)
        return {"ingredients": ingredients, "recette": result}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération de la recette : {e}"
        )

@router.get("/ask")
def ask_general(
    question: str = Query(..., description="Question à poser à l'IA")
):
    """
    Permet d’envoyer une question libre à Gemini.
    Exemple : /api/ai/ask?question=Explique la mécanique quantique simplement
    """
    try:
        result = ask_gemini(question)
        return {"question": question, "réponse": result}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la requête à Gemini : {e}"
        )
