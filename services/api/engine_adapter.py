# engine_adapter.py
from __future__ import annotations

from datetime import date, datetime
from typing import Dict, List

from models import (
    CalcInput,
    Card,
    Profile,
    CoreNumbers,
    FourElements,
    TriangleAges,
    TriangleNumbers,
    Unions,
    Grid,
    ExtraInfo,
)

# ====== 共用小工具 ======

LETTER_MAP: Dict[str, int] = {}
_groups = {
    1: "AJS",
    2: "BKT",
    3: "CLU",
    4: "DMV",
    5: "ENW",
    6: "FOX",
    7: "GPY",
    8: "HQZ",
    9: "IR",
}
for num, chars in _groups.items():
    for ch in chars:
        LETTER_MAP[ch] = num

VOWELS = set("AEIOU")


def _digit_sum(n: int) -> int:
    return sum(int(d) for d in str(abs(n)))


def _reduce_with_master(n: int) -> int:
    """保留 11/22/33，其他數字一直拆到 1–9。"""
    while n > 9 and n not in (11, 22, 33):
        n = _digit_sum(n)
    return n


# ====== 5 大核心數字 ======

def _calc_life_path(birth: date) -> (int, int):
    digits = [int(ch) for ch in birth.strftime("%Y%m%d")]
    raw = sum(digits)          # 例如 38
    core = _reduce_with_master(raw)  # 例如 11
    return raw, core


def _name_to_numbers(name: str) -> List[int]:
    return [LETTER_MAP.get(ch, 0) for ch in name.upper() if ch.isalpha()]


def _reduce_list(nums: List[int]) -> (int, int):
    raw = sum(nums)
    core = _reduce_with_master(raw)
    return raw, core


def _calc_destiny(name: str) -> (int, int):
    nums = _name_to_numbers(name)
    return _reduce_list(nums)


def _calc_soul_and_personality(name: str) -> ((int, int), (int, int)):
    nums_vowel = [
        LETTER_MAP[ch]
        for ch in name.upper()
        if ch.isalpha() and ch in VOWELS
    ]
    nums_cons = [
        LETTER_MAP[ch]
        for ch in name.upper()
        if ch.isalpha() and ch not in VOWELS
    ]
    soul_raw, soul_core = _reduce_list(nums_vowel) if nums_vowel else (0, 0)
    per_raw, per_core = _reduce_list(nums_cons) if nums_cons else (0, 0)
    return (soul_raw, soul_core), (per_raw, per_core)


def _calc_maturity(life_path_core: int, destiny_core: int) -> (int, int):
    raw = life_path_core + destiny_core
    core = _reduce_with_master(raw)
    return raw, core


def compute_core_numbers(name: str, birth: date) -> CoreNumbers:
    lp_raw, lp = _calc_life_path(birth)
    dest_raw, dest = _calc_destiny(name)
    (soul_raw, soul_core), (per_raw, per_core) = _calc_soul_and_personality(name)
    mat_raw, mat = _calc_maturity(lp, dest)

    return CoreNumbers(
        life_path=lp,
        life_path_raw=lp_raw,
        destiny=dest,
        destiny_raw=dest_raw,
        soul=soul_core,
        soul_raw=soul_raw,
        personality=per_core,
        personality_raw=per_raw,
        maturity=mat,
        maturity_raw=mat_raw,
    )


# ====== 其他區塊（先用簡化版，之後再升級） ======

def compute_four_elements(core: CoreNumbers) -> FourElements:
    """
    這裡暫時用一個『可解釋』但簡單的規則：
    - 身體 Body     = life_path 的一位數（38→3+8=11→1+1=2）
    - 頭腦 Mind     = destiny 的一位數
    - 情緒 Emotion  = soul 的一位數
    - 直覺 Intuition= personality 的一位數
    之後你要換成「補5規則、Y 母音規則」那一套時，只要改這裡即可。
    """
    def one_digit(n: int) -> int:
        x = _reduce_with_master(n)
        # 如果是 11 / 22 / 33，再拆一次變一位數
        if x in (11, 22, 33):
            x = _digit_sum(x)
        return x

    return FourElements(
        body=one_digit(core.life_path),
        mind=one_digit(core.destiny),
        emotion=one_digit(core.soul),
        intuition=one_digit(core.personality),
    )


def compute_triangle_ages(birth: date) -> TriangleAges:
    """
    暫定：
    - early  = 0–28
    - middle = 29–56
    - late   = 57+
    之後你可以改成你想要的年齡切法。
    """
    return TriangleAges(early=28, middle=56, late=99)


def compute_triangle_numbers(core: CoreNumbers) -> TriangleNumbers:
    """
    暫定用：
    - early  = life_path
    - middle = destiny
    - late   = maturity
    純粹先給前端有東西可以畫圖。
    """
    return TriangleNumbers(
        early=core.life_path,
        middle=core.destiny,
        late=core.maturity,
    )


def compute_unions(core: CoreNumbers) -> Unions:
    """
    這裡先放示意資料。未來你可以把「聯盟數字」真正的組合表搬進來。
    """
    return Unions(
        early=[f"{core.life_path}{core.destiny}"],
        middle=[f"{core.soul}{core.personality}"],
        late=[str(core.maturity)],
    )


def compute_grid(name: str, birth: date) -> Grid:
    """
    簡單版九宮格：
    - 把生日數字 + 姓名字母數字全部丟進去數次數。
    """
    counts = {str(i): 0 for i in range(1, 10)}

    # 生日數字
    for ch in birth.strftime("%Y%m%d"):
        if ch.isdigit() and ch != "0":
            counts[ch] += 1

    # 姓名字母
    for n in _name_to_numbers(name):
        if n != 0:
            counts[str(_reduce_with_master(n))] += 1

    missing = [int(k) for k, v in counts.items() if v == 0]

    return Grid(counts=counts, missing=missing)


# ====== 將所有東西組成一張 Card ======

def build_card(payload: CalcInput) -> Card:
    # 1. 核心數字
    core = compute_core_numbers(payload.name, payload.birth)

    # 2. Profile
    today = datetime.today().date()
    age = today.year - payload.birth.year - (
        (today.month, today.day) < (payload.birth.month, payload.birth.day)
    )

    life_path_text = f"{core.life_path_raw}→{core.life_path}"

    profile = Profile(
        name=payload.name,
        display_name=None,
        birth=payload.birth,
        gender=payload.gender,
        age=age,
        life_path_text=life_path_text,
    )

    # 3. 其他區塊
    four = compute_four_elements(core)
    tri_ages = compute_triangle_ages(payload.birth)
    tri_nums = compute_triangle_numbers(core)
    unions = compute_unions(core)
    grid = compute_grid(payload.name, payload.birth)
    extra = ExtraInfo(
        note="demo 版引擎：核心數字為正式算法，其餘區塊可以之後再替換為喬鈞正式規則。",
        raw_data={},
    )

    return Card(
        profile=profile,
        core_numbers=core,
        four_elements=four,
        triangle_ages=tri_ages,
        triangle_numbers=tri_nums,
        unions=unions,
        grid=grid,
        extra=extra,
    )


def compute_all(payload: CalcInput):
    """
    給 main.py 用的介面。
    目前只回傳 Card，外層 request_id / engine_version 在 main 裡組。
    """
    card = build_card(payload)
    return card
