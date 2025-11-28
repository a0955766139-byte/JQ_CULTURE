<!-- .github/copilot-instructions.md - guidance for AI coding agents -->

# 快速上手（給 AI 編碼助理）

本檔案以簡短、具體的指示讓 AI 助手能快速在此 codebase 中做變更或補丁。優先檔案：`services/api/*`。

## 核心概覽（Big picture）
- 服務：`services/api` 是一個用 FastAPI 建的 demo API，主要職責是接收前端請求並回傳一張「數字卡」物件。
- 計算引擎：`engine_adapter.py` 包含主要的計算邏輯（字母->數字映射、核心數字、九宮格等）。
- 資料模型：`models.py`（CalcInput / CalcResponse / Card / CoreNumbers...）與 `models_user.py`（使用者、日記模型）。
- 假資料存取：`storage_in_memory.py` 是一個進程內的暫存 DB（單一 demo user，`FIXED_USER_ID`），用於 profile/journal endpoints。
- 入口：`main.py` 定義 API 路由（計算、會員、日記）並呼叫 `compute_all` 組裝 `CalcResponse`。

## 重要檔案與責任範圍（quick links）
- `services/api/main.py`：API 路由、健康檢查、`/api/v1/calc` 的外層 response 組裝。
- `services/api/engine_adapter.py`：演算法實作；若要改計算規則或加入正式資料表，修改此檔。
- `services/api/models.py`：Pydantic schema，所有回傳/請求結構在此定義，修改欄位會影響 API response model。
- `services/api/models_user.py`：user/journal schema 與 input models。
- `services/api/storage_in_memory.py`：示範用的暫存，真實 DB 整合時可替換此模組（保持相同 function 名稱接口）。
- `client_calc.py`：範例 client，但目前與實際 response 結構有 mismatch（client 期待 `numbers`，實際回傳為 `card`），修改或移除前請確認。

## 在本 repo 常見的實作模式 / 注意事項
- 版本與規則：`CalcInput.ruleset` 用來標記計算規則版本（例如 `jq_default_tw`），若要新增 A/B 規則切換，優先在 `engine_adapter` 新增分支處理。
- 不要在 `main.py` 寫複雜邏輯：它只應該做 request/response 包裝，實際計算放 `engine_adapter.py`。
- `storage_in_memory.py` 是狀態性（process-local）存放，測試或 demo 用：若要接資料庫，請替換整個 module，保持相同函式簽章（`get_or_create_user`, `update_user`, `save_journal`, `get_journal`, `list_journals`）。
- 字母映射與「保留 master numbers (11/22/33)」等 domain 規則寫在 helper 函式（例如 `_reduce_with_master`），調整規則時優先修改這些 helper。

## 本機開發 / 執行指令（確保在專案 root 或 `services/api`）
- 建議使用 virtualenv；如果沒有 `requirements.txt`，預估需要：`fastapi`, `uvicorn`, `pydantic`, `requests`（用於 `client_calc.py`）。

示例步驟：
```bash
# 在專案根目錄
python3 -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn pydantic requests

# 啟動 API（工作目錄：services/api）
cd services/api
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

API health 檢查：`GET http://127.0.0.1:8000/health`

呼叫主要路由（JSON 範例）:
POST `http://127.0.0.1:8000/api/v1/calc`
```json
{ "name": "YUCHIAOCHUN", "birth": "1983-09-08", "gender": "F" }
```

注意：client 範例 `client_calc.py` 需要修正以讀 `card` 裡的欄位（目前程式嘗試讀 `numbers`）。

## 編輯建議與範例任務
- 若要更新計算規則（例如加入「Y 母音規則」或改分組映射）：修改 `engine_adapter.py` 中對應 helper（`LETTER_MAP`, `VOWELS`, `_reduce_with_master`）並加單元測試。
- 若要替換資料存取層：新增 `services/api/storage_sql.py`（或相同介面）並在 `main.py` 中以輕量工廠替換 `import storage_in_memory as store`。
- 若要更新 response schema：先改 `models.py` 的 Pydantic 類別，然後在 `main.py`/`engine_adapter.py` 補齊相應欄位，確保 `response_model` 與實際回傳一致。

## 已知問題 / quirks（可直接驗證）
- `client_calc.py` 與 `models.py` 不一致（client 解析 `numbers`，實際回傳 `card`）——在修復 PR 中務必同步更新範例或 models。
- 無 `requirements.txt`。在 PR 中新增 dependencies 或 `requirements.txt` 會有助於 CI 與新 contributor。

## 提交 PR 建議
- 小改動（algorithm / schema）：在 PR 描述中註明影響的 endpoint 與 schema，並包含一個簡短的手動驗證步驟（例如 curl / sample payload）。
- 若改動 model schema，請同時更新或新增一個 small example client（可在 `client_calc.py` 內示範如何解析新版 response）。

-- 需要我把這份檔案調整為英文版或補上 `requirements.txt` 範例嗎？
