# services/api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

# Routers
from services.api.routes.health_router import router as health_router
from services.api.routes.user_router import router as user_router
from services.api.routes.journal_router import router as journal_router
from services.api.routes.mission_router import router as mission_router
from services.api.routes.card_router import router as card_router

app = FastAPI(
    title="JQ Culture API",
    version="1.0.0",
)

# CORS（先全開，正式上線再收斂到你的前端網域）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 根路徑（避免 404；也可改成導向 /docs）
@app.get("/", include_in_schema=False)
def index():
    return {"service": "JQ Culture API", "status": "ok"}

# 掛載 Routers
app.include_router(health_router)
app.include_router(user_router)
app.include_router(journal_router)
app.include_router(mission_router)
app.include_router(card_router)
