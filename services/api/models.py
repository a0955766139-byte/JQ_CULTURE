# models.py
from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional, Literal

from pydantic import BaseModel, Field


# ========= 請求模型 =========

class CalcInput(BaseModel):
    """前端送進來的主計算輸入。"""
    name: str = Field(..., description="姓名（英文或中文皆可）")
    birth: date = Field(..., description="出生日期，格式：YYYY-MM-DD")
    gender: Literal["F", "M", "O", "U"] = Field(
        "F",
        description="性別：F=女性, M=男性, O=其他, U=未知"
    )
    ruleset: str = Field(
        "jq_default_tw",
        description="計算規則版本，用來之後做 A/B 規則切換"
    )


# ========= 卡片內層各區塊 =========

class Profile(BaseModel):
    """個人基本資料＋簡單說明文字。"""
    name: str
    display_name: Optional[str] = None
    birth: date
    gender: str
    age: int
    life_path_text: str = Field(
        ...,
        description="例如：'38→11→11' 或 '3811/2'，給前端顯示用"
    )


class CoreNumbers(BaseModel):
    """五大核心數字。"""
    life_path: int
    life_path_raw: int

    destiny: int
    destiny_raw: int

    soul: int
    soul_raw: int

    personality: int
    personality_raw: int

    maturity: int
    maturity_raw: int


class FourElements(BaseModel):
    """四象限（身／腦／情／直覺）。暫時先用簡單計算，之後可換成正式規則。"""
    body: int
    mind: int
    emotion: int
    intuition: int


class TriangleAges(BaseModel):
    """三階段年齡區間。"""
    early: int
    middle: int
    late: int


class TriangleNumbers(BaseModel):
    """三階段能量數。"""
    early: int
    middle: int
    late: int


class Unions(BaseModel):
    """聯盟數字（之後可以放你整理的 12 組 / 36 組組合）。"""
    early: List[str] = []
    middle: List[str] = []
    late: List[str] = []


class Grid(BaseModel):
    """數字九宮格：每個數字出現次數＋缺數。"""
    counts: Dict[str, int] = Field(
        default_factory=dict,
        description="key='1'~'9', value=出現次數"
    )
    missing: List[int] = Field(
        default_factory=list,
        description="缺少的數字列表"
    )


class ExtraInfo(BaseModel):
    """預留給之後加欄位用的彈性區塊。"""
    note: Optional[str] = None
    raw_data: Dict[str, Any] = Field(default_factory=dict)


class Card(BaseModel):
    """一張完整的『喬鈞文化數字卡』結構。"""
    profile: Profile
    core_numbers: CoreNumbers
    four_elements: FourElements
    triangle_ages: TriangleAges
    triangle_numbers: TriangleNumbers
    unions: Unions
    grid: Grid
    extra: ExtraInfo = ExtraInfo()


# ========= 回傳模型 =========

class CalcResponse(BaseModel):
    """API 回傳的最外層結構。"""
    request_id: int
    engine_version: str = "0.2.0"
    ruleset: str
    card: Card
