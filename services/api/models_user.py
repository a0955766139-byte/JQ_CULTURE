# models_user.py
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class UserProfile(BaseModel):
    """會員基本資料（簡化版）"""
    user_id: str = Field(..., description="系統內部用的會員代號")
    name: Optional[str] = None          # 真實姓名
    display_name: Optional[str] = None  # 顯示暱稱
    birth: Optional[date] = None
    gender: Optional[str] = None        # "F" / "M" / 其他
    email: Optional[str] = None
    phone: Optional[str] = None


class UserProfileUpdate(BaseModel):
    """修改會員資料時用的輸入模型"""
    name: Optional[str] = None
    display_name: Optional[str] = None
    birth: Optional[date] = None
    gender: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class JournalEntry(BaseModel):
    """一筆日記紀錄"""
    user_id: str
    date: date               # 這篇日記是哪一天的
    title: str               # 日記標題
    content: str             # 內容
    mood: Optional[int] = Field(
        None,
        ge=1,
        le=5,
        description="心情 1~5 分，可以空白"
    )
    tags: List[str] = []     # 關鍵字標籤
    has_checkin: bool = True # 是否算打卡
    card_name: Optional[str] = None   # 牌名（例如：內在小孩）
    card_note: Optional[str] = None   # 提醒語、關鍵訊息
    created_at: datetime
    updated_at: datetime


class JournalEntryCreate(BaseModel):
    """前端送進來要新增／更新日記時用"""
    date: date
    title: str
    content: str
    mood: Optional[int] = Field(None, ge=1, le=5)
    tags: List[str] = []
    has_checkin: bool = True


class JournalListResponse(BaseModel):
    """列出某個月份的日記列表"""
    items: List[JournalEntry]
# services/api/models_user.py
from typing import List, Optional
from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    """會員基本資料（目前先假裝只有一個 demo 使用者）"""

    user_id: str = "demo-user-1"
    name: Optional[str] = None          # 真實姓名
    display_name: Optional[str] = None  # 顯示暱稱
    birth: Optional[str] = None         # 生日 YYYY-MM-DD
    gender: Optional[str] = None        # "M" / "F" / "O"...
    email: Optional[str] = None
    phone: Optional[str] = None
    note: Optional[str] = None          # 備註／教練筆記


class UserProfileUpdate(BaseModel):
    """更新會員資料時用的欄位（全部都可選）"""

    name: Optional[str] = None
    display_name: Optional[str] = None
    birth: Optional[str] = None
    gender: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    note: Optional[str] = None


class JournalEntryCreate(BaseModel):
    """寫日記時，前端要送進來的欄位"""

    title: str
    content: str
    mood: int = Field(ge=1, le=10, description="心情分數 1~10")
    tags: List[str] = []
    date: str  # "YYYY-MM-DD"


class JournalEntry(BaseModel):
    """儲存在系統裡的一篇日記"""

    user_id: str
    date: str
    title: str
    content: str
    mood: int
    tags: List[str] = []
    has_checkin: bool = True
    created_at: str
    updated_at: str


class JournalListItem(BaseModel):
    """日記列表用的精簡欄位"""

    date: str
    title: str
    mood: int


class JournalListResponse(BaseModel):
    """日記列表回應"""

    items: List[JournalListItem]
# ======== 首頁 Home 區塊 ========

class HomeSection(BaseModel):
    """首頁上的一個功能卡片（六大系統之一）"""
    code: str              # 例如：cards / calc / journal / coaching / store / profile
    title: str             # 卡片主標題
    subtitle: str          # 副標／簡短說明
    cta: str               # 按鈕文字（Call To Action）
    front_route: str       # 前端畫面的路由，例如 /cards
    api_entry: str         # 主要會呼叫的 API path，例如 /api/v1/cards/random
    need_login: bool       # 是否需要登入才看得到／使用


class HomeResponse(BaseModel):
    """首頁 API 回傳的整體結構"""
    user: Dict[str, Any]           # 使用者區塊（是否登入、名字、今天日期）
    sections: List[HomeSection]    # 六大系統卡片列表
