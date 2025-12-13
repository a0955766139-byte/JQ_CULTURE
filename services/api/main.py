from fastapi import FastAPI
from services.api.routes.health_router import router as health_router
from services.api.routes.user_router import router as user_router
from services.api.routes.journal_router import router as journal_router
from services.api.routes.mission_router import router as mission_router
from services.api.routes.card_router import router as card_router

app = FastAPI(title="JQ Culture API", version="1.0.0")

# 掛載 Routers
app.include_router(health_router)
app.include_router(user_router)
app.include_router(journal_router)
app.include_router(mission_router)
app.include_router(card_router)
