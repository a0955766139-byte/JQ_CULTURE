from fastapi import APIRouter

router = APIRouter(prefix="/journals", tags=["journals"])

@router.get("/")
def list_journals():
    return {"message": "journals ok"}
