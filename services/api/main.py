# services/api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

# === Routers ===
from services.api.routes.health_router import router as health_router
from services.api.routes.user_router import router as user_router
from services.api.routes.journal_router import router as journal_router
from services.api.routes.mission_router import router as mission_router
from services.api.routes.card_router import router as card_router
# from services.api.routes.auth_routes import router as auth_router  # 尚未就緒先關閉

app = FastAPI(
    title="JQ Culture API",
    version="1.0.0",
)

# === CORS（先全面開放；上線後建議改成你的前端網域） ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # 之後改成 ["https://your-frontend.domain"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === 根路徑（兩選一：A 顯示狀態；B 直接導向 /docs） ===
@app.get("/", include_in_schema=False)
def root():
    return {"service": "JQ Culture API", "status": "ok"}

# 若你想改成自動導向 Swagger，改用下面這段，並把上面的 root 註解掉
# @app.get("/", include_in_schema=False)
# def root_redirect():
#     return RedirectResponse(url="/docs")

# === 掛載 Routers ===
app.include_router(health_router)
app.include_router(user_router)
app.include_router(journal_router)
app.include_router(mission_router)
app.include_router(card_router)
# app.include_router(auth_router)
