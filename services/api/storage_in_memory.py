# storage_in_memory.py
from datetime import datetime
from typing import Dict, Tuple, List, Optional

from models_user import UserProfile, UserProfileUpdate, JournalEntry, JournalEntryCreate
from models_cards import CardDefinition
import random

# 假裝的資料庫：程式關掉就會清空
USERS: Dict[str, UserProfile] = {}
JOURNALS: Dict[Tuple[str, str], JournalEntry] = {}  # key: (user_id, "YYYY-MM-DD")

# 目前先假裝只有一個登入中的學員
FIXED_USER_ID = "demo-user-1"


def get_or_create_user() -> UserProfile:
    """如果沒這個會員，就幫他建一個空白的 profile。"""
    if FIXED_USER_ID not in USERS:
        USERS[FIXED_USER_ID] = UserProfile(user_id=FIXED_USER_ID)
    return USERS[FIXED_USER_ID]


def update_user(update: UserProfileUpdate) -> UserProfile:
    """更新會員基本資料（只改有給值的欄位）。"""
    profile = get_or_create_user()
    data = update.dict(exclude_unset=True)
    new_profile = profile.copy(update=data)
    USERS[FIXED_USER_ID] = new_profile
    return new_profile


def save_journal(payload: JournalEntryCreate) -> JournalEntry:
    """新增或覆蓋某一天的日記。"""
    now = datetime.utcnow()
    key = (FIXED_USER_ID, payload.date.isoformat())

    existing = JOURNALS.get(key)
    if existing:
        entry = existing.copy(
            update={
                "title": payload.title,
                "content": payload.content,
                "mood": payload.mood,
                "tags": payload.tags,
                "has_checkin": payload.has_checkin,
                "updated_at": now,
            }
        )
    else:
        entry = JournalEntry(
            user_id=FIXED_USER_ID,
            date=payload.date,
            title=payload.title,
            content=payload.content,
            mood=payload.mood,
            tags=payload.tags,
            has_checkin=payload.has_checkin,
            card_name=payload.card_name,
        card_note=payload.card_note,
            created_at=now,
            updated_at=now,
        )

    JOURNALS[key] = entry
    return entry


def get_journal(date_str: str) -> Optional[JournalEntry]:
    """取得某一天的日記。date_str 格式：YYYY-MM-DD"""
    key = (FIXED_USER_ID, date_str)
    return JOURNALS.get(key)


def list_journals(month_prefix: str) -> List[JournalEntry]:
    """
    列出某個月份的所有日記。
    month_prefix 例如 '2025-11'
    """
    result: List[JournalEntry] = []
    for (uid, d), entry in JOURNALS.items():
        if uid != FIXED_USER_ID:
            continue
        if d.startswith(month_prefix):
            result.append(entry)

    # 依日期排序
    result.sort(key=lambda e: e.date)
    return result
# services/api/storage_in_memory.py
from datetime import datetime
from typing import Dict, List, Optional

from models_user import (
    UserProfile,
    UserProfileUpdate,
    JournalEntry,
    JournalEntryCreate,
    JournalListItem,
    JournalListResponse,
)

# 先假裝只有一個使用者
_profile: Optional[UserProfile] = None
# key = "YYYY-MM-DD"
_journals: Dict[str, JournalEntry] = {}


def _now_iso() -> str:
    """回傳現在時間（UTC）的 ISO 字串"""
    return datetime.utcnow().isoformat()


# ＝＝＝＝＝ 會員資料相關 ＝＝＝＝＝

def get_or_create_user() -> UserProfile:
    """如果沒有會員資料，就建立一份空的；有的話就直接回傳。"""
    global _profile
    if _profile is None:
        _profile = UserProfile()
    return _profile


def update_user(payload: UserProfileUpdate) -> UserProfile:
    """更新會員資料（只有有給值的欄位才會更新）"""
    global _profile
    if _profile is None:
        _profile = UserProfile()

    data = _profile.dict()
    for field, value in payload.dict(exclude_unset=True).items():
        data[field] = value

    _profile = UserProfile(**data)
    return _profile


# ＝＝＝＝＝ 日記相關 ＝＝＝＝＝

def save_journal(payload: JournalEntryCreate) -> JournalEntry:
    """新增或覆蓋某一天的日記"""
    user = get_or_create_user()
    now = _now_iso()

    # 如果這一天已經有日記，沿用原本的 created_at
    if payload.date in _journals:
        created_at = _journals[payload.date].created_at
    else:
        created_at = now

    entry = JournalEntry(
        user_id=user.user_id,
        date=payload.date,
        title=payload.title,
        content=payload.content,
        mood=payload.mood,
        tags=payload.tags,
        has_checkin=True,
        created_at=created_at,
        updated_at=now,
    )

    _journals[payload.date] = entry
    return entry


def list_journals(month: str) -> JournalListResponse:
    """
    列出某個月份的所有日記（例如 month = "2025-11"）
    """
    items: List[JournalListItem] = []

    for date, entry in sorted(_journals.items()):
        if date.startswith(month):
            items.append(
                JournalListItem(
                    date=entry.date,
                    title=entry.title,
                    mood=entry.mood,
                )
            )

    return JournalListResponse(items=items)


def get_journal(date: str) -> Optional[JournalEntry]:
    """取得某一天的日記；如果沒有就回傳 None"""
    return _journals.get(date)
# =====================================================
# ===== 牌卡：只存牌義，不存抽牌紀錄 =====
from typing import Dict, List
import random

from models_cards import CardDefinition

CARD_DECK: Dict[str, CardDefinition] = {}


def _load_default_cards() -> None:
    """初始化一組 demo 牌組。未來可以改成從資料庫 / JSON 載入。"""
    global CARD_DECK
    if CARD_DECK:   # 已經載過就不要重複做
        return

    base_url = "https://example.com/jq_cards"

    seed_cards = [
        CardDefinition(
            code="JQ-001",
            name="內在孩童",
            short_title="允許脆弱",
            description="當你願意看見自己的害怕、委屈與不安時，力量才會回來。",
            keywords=["接納", "溫柔", "真實"],
            image_url=f"{base_url}/jq_001.png",
            suit="心靈",
            element="水",
            recommend_use="覺察情緒、寫日記前抽",
        ),
        CardDefinition(
            code="JQ-002",
            name="界線之光",
            short_title="說出不行",
            description="真正的溫柔，包含清楚地說『不』。",
            keywords=["界線", "責任", "尊重"],
            image_url=f"{base_url}/jq_002.png",
            suit="行動",
            element="火",
            recommend_use="準備談合作、溝通前抽",
        ),
        CardDefinition(
            code="JQ-003",
            name="靜心之門",
            short_title="慢一點",
            description="當你願意放慢腳步，內在的聲音才有機會被你聽見。",
            keywords=["靜心", "停下來", "內觀"],
            image_url=f"{base_url}/jq_003.png",
            suit="靈性",
            element="風",
            recommend_use="感到焦慮、急躁時使用",
        ),
    ]

    CARD_DECK = {c.code: c for c in seed_cards}


def list_all_cards() -> List[CardDefinition]:
    """取得整副牌（之後可以給後台管理用）"""
    _load_default_cards()
    return list(CARD_DECK.values())


from typing import Optional  # 如果上面沒有，就補這個

def get_card(code: str) -> Optional[CardDefinition]:
    """給 /api/v1/cards/{code} 查單張用"""
    _load_default_cards()
    return CARD_DECK.get(code)


def draw_random_card() -> CardDefinition:
    """隨機抽一張牌，不儲存抽牌紀錄"""
    cards = list_all_cards()

    if not cards:
        # 這個錯誤如果發生，會變成 500，但訊息就會很明確：牌組是空的
        raise RuntimeError("Card deck is empty, please configure seed cards.")

    return random.choice(cards)

