from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

# 一數字心理學主運算 ===
from models import CalcInput, CalcResponse
from engine_adapter import compute_all

# 會員中心 & 日記的 model
from models_user import (
    UserProfile,
    UserProfileUpdate,
    JournalEntry,
    JournalEntryCreate,
    JournalListResponse,
    HomeSection,
    HomeResponse,
)

# 牌卡用的 model
from models_cards import CardDefinition, CardDrawResponse, CardListResponse
import storage_in_memory as store


from datetime import datetime



app = FastAPI(
    title="JQ Culture Numerology API",
    version="0.2.0",
    description="喬鈞文化 × 現代數字心理學 API（demo 版，含會員中心＋日記）",
)

BASE_DIR = Path(__file__).parent

@app.get("/", include_in_schema=False)
def serve_index():
    """回傳首頁 HTML（手機版 Web App）"""
    index_path = BASE_DIR / "static" / "index.html"
    return FileResponse(index_path)


# ＝＝＝＝＝ 健康檢查 ＝＝＝＝＝

@app.get("/health")
def health():
    return {"status": "ok"}


# ＝＝＝＝＝ 數字心理學：主計算入口 ＝＝＝＝＝

@app.post("/api/v1/calc", response_model=CalcResponse)
def calc(payload: CalcInput):
    """
    主計算入口：
    目前仍使用你原本的 compute_all 規則，
    回傳生命靈數九宮格等資料。
    """
    card = compute_all(payload)

    return CalcResponse(
        request_id=1,            # demo 先寫死
        engine_version="0.2.0",  # 之後每次改版可以自己更新
        ruleset=payload.ruleset,
        card=card,
    )


# ＝＝＝＝＝ 會員中心：基本資料 ＝＝＝＝＝

@app.get("/api/v1/me/profile", response_model=UserProfile)
def get_my_profile():
    """取得目前登入者的基本資料（現在先假裝只有 demo-user-1）"""
    return store.get_or_create_user()


@app.put("/api/v1/me/profile", response_model=UserProfile)
def update_my_profile(payload: UserProfileUpdate):
    """更新目前登入者的基本資料"""
    return store.update_user(payload)


# ＝＝＝＝＝ 會員中心：日記與打卡 ＝＝＝＝＝

@app.post("/api/v1/me/journal", response_model=JournalEntry)
def write_journal(payload: JournalEntryCreate):
    """
    寫一篇日記：
    - 如果該日期已經有日記，就視為覆蓋更新
    - mood 必須是 1~5 的整數
    """
    return store.save_journal(payload)


@app.get("/api/v1/me/journal", response_model=JournalListResponse)
def list_my_journals(month: str):
    """
    列出某個月份的日記列表。
    month 例： "2025-11"
    """
    return store.list_journals(month)


@app.get("/api/v1/me/journal/{date}", response_model=JournalEntry)
def get_journal_by_date(date: str):
    """
    取得某一天的日記內容。
    date 格式：YYYY-MM-DD
    """
    entry = store.get_journal(date)
    if not entry:
        raise HTTPException(status_code=404, detail="Journal not found")
    return entry
# ======== 首頁 Home API ========

@app.get("/api/v1/home", response_model=HomeResponse)
def get_home():
    """首頁總覽：
    - 回傳使用者簡單資訊
    - 回傳六大系統的卡片列表
    """
    # 先拿目前的 demo 使用者資料
    user = store.get_or_create_user()

    user_block = {
        "is_logged_in": True,
        "name": user.name or "喬鈞文化會員",
        "today": datetime.now().strftime("%Y-%m-%d"),
    }

    sections = [
        HomeSection(
            code="cards",
            title="每日抽牌卡",
            subtitle="用一張牌，看見今天的提醒",
            cta="開始抽牌",
            front_route="/cards",
            api_entry="/api/v1/cards/random",
            need_login=False,
        ),
        HomeSection(
            code="calc",
            title="數字心理學測評",
            subtitle="輸入姓名與生日，啟動你的靈魂地圖",
            cta="開始測評",
            front_route="/calc",
            api_entry="/api/v1/calc",
            need_login=False,
        ),
        HomeSection(
            code="journal",
            title="顯化日記中心",
            subtitle="每天 3 分鐘，寫下你的內在對話",
            cta="寫今天的日記",
            front_route="/me/journal",
            api_entry="/api/v1/me/journal",
            need_login=True,
        ),
        HomeSection(
            code="coaching",
            title="個案 1v1 解析",
            subtitle="專屬於你的深度解盤與陪伴",
            cta="查看方案",
            front_route="/coaching",
            api_entry="/api/v1/coaching/packages",
            need_login=False,
        ),
        HomeSection(
            code="store",
            title="喬鈞選書與課程",
            subtitle="把課帶回家，讓練習變成日常",
            cta="進入商城",
            front_route="/store",
            api_entry="/api/v1/store/products",
            need_login=False,
        ),
        HomeSection(
            code="profile",
            title="我的專屬資料",
            subtitle="整理你的數字、備註、紀錄",
            cta="查看個人檔案",
            front_route="/me/profile",
            api_entry="/api/v1/me/profile",
            need_login=True,
        ),
    ]

    return HomeResponse(user=user_block, sections=sections)
# ===== 抽牌卡 API =====

@app.get("/api/v1/cards/random", response_model=CardDrawResponse)
def draw_card():
    """抽一張牌，不存任何歷史紀錄"""
    card = store.draw_random_card()
    return CardDrawResponse(
        request_id=1,
        deck_version="1.0.0",
        card=card,
    )


@app.get("/api/v1/cards/{code}", response_model=CardDefinition)
def get_card_by_code(code: str):
    """用代碼查一張牌（之後前端點擊卡片細節可以用）"""
    card = store.get_card(code)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card
