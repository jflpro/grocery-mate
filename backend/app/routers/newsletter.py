from fastapi import APIRouter, HTTPException
from app.utils.mail import send_newsletter

router = APIRouter(
    prefix="/newsletter",
    tags=["Newsletter"]
)

@router.post("/send")
def send_newsletter_email(to_email: str):
    """
    Envoie une newsletter avec le header List-Unsubscribe.
    """
    try:
        send_newsletter(
            to_email=to_email,
            subject="Newsletter GroceryMate",
            body="Bonjour, voici votre newsletter avec désabonnement automatique."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'envoi du mail : {str(e)}")
    
    return {"message": f"Newsletter envoyée à {to_email}"}

