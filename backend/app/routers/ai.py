from fastapi import APIRouter, Query, HTTPException
from app.gemini_service import ask_gemini

# ✅ Router without local prefix — the /api/ai prefix is added in main.py
router = APIRouter(tags=["AI"])


@router.get("/recipe")
def generate_recipe(
    ingredients: str = Query(
        ...,
        description="Comma-separated list of ingredients"
    )
):
    """
    Generate a simple recipe based on a list of ingredients.

    Example:
        /api/ai/recipe?ingredients=chicken,carrots,rice
    """
    prompt = (
        f"Generate a simple and appetizing recipe in English using these ingredients: {ingredients}."
    )

    try:
        result = ask_gemini(prompt)
        # NOTE: Keep the JSON keys for backward compatibility with the frontend
        return {"ingredients": ingredients, "recette": result}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error while generating the recipe: {e}"
        )


@router.get("/ask")
def ask_general(
    question: str = Query(
        ...,
        description="Question to ask the AI"
    )
):
    """
    Send a free-form question to Gemini.

    Example:
        /api/ai/ask?question=Explain quantum mechanics in simple terms
    """
    try:
        result = ask_gemini(question)
        # NOTE: Keep the JSON keys for backward compatibility with the frontend
        return {"question": question, "réponse": result}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error while sending the request to Gemini: {e}"
        )
