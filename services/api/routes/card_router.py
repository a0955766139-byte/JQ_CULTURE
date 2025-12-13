from fastapi import APIRouter

router = APIRouter(prefix="/cards", tags=["cards"])

@router.get("/")
def list_cards():
    return {"message": "cards ok"}
