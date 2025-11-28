# models_cards.py
from typing import List, Optional
from pydantic import BaseModel


class CardDefinition(BaseModel):
    code: str               # 牌的代碼，例如 JQ-001
    name: str               # 牌名
    short_title: str        # 短標題（精華）
    description: str        # 完整說明
    keywords: List[str]     # 關鍵字
    image_url: str          # 圖片網址
    suit: Optional[str] = None
    element: Optional[str] = None
    recommend_use: Optional[str] = None   # 建議使用情境


class CardDrawResponse(BaseModel):
    request_id: int
    deck_version: str
    card: CardDefinition


class CardListResponse(BaseModel):
    cards: List[CardDefinition]
