from fastapi import APIRouter

router = APIRouter(prefix="/missions", tags=["missions"])

@router.get("/")
def list_missions():
    return {"message": "missions ok"}
