# FastAPI + HTMX 新聞網站開發路線圖

## 架構概覽

```
首頁 → 新聞列表 → 文章詳情
         ↑
   HTMX 搜尋 / 無限捲動
         ↑
   SQLite 資料庫 (SQLAlchemy)
         ↑
   RSS 爬蟲定時匯入
         ↑
   分類 / 標籤 / 分頁
         ↑
   管理後台
         ↑
   快取 + Docker 部署
```

## 升級步驟

每一步完成後皆為可執行狀態。

---

### Step 1 — 專案骨架 + 首頁

**目標：** FastAPI 能啟動，首頁回傳 HTML。

**專案結構：**

```
news_net/
├── main.py
├── requirements.txt
└── templates/
    └── index.html
```

**技術重點：**

- 依賴：`fastapi`、`uvicorn`、`jinja2`
- 首頁路由 `GET /` 回傳 Jinja2 模板
- 基礎 HTML 版型（Header / Footer）

**啟動指令：**

```bash
uvicorn main:app --reload
```

---

### Step 2 — 靜態假資料 + 新聞列表頁

**目標：** 首頁顯示新聞卡片列表，點入可看文章詳情頁。

**新增檔案：**

```
news_net/
├── routers/
│   └── news.py          # 新聞路由
├── schemas.py           # Pydantic 資料模型
└── templates/
    ├── base.html        # 共用版型
    ├── index.html
    └── article.html     # 文章詳情頁
```

**技術重點：**

- `NewsItem` Pydantic schema 定義欄位
- Python list 當假資料庫（無需 DB）
- Jinja2 模板繼承 `base.html`

---

### Step 3 — SQLite 資料庫 + SQLAlchemy

**目標：** 新聞資料存進 DB，支援建立 / 讀取。

**新增檔案：**

```
news_net/
├── database.py          # DB 連線設定
├── models.py            # SQLAlchemy ORM 模型
└── crud.py              # 資料庫操作函式
```

**技術重點：**

- 依賴：`sqlalchemy`、`aiosqlite`（非同步）
- `Article` 資料表欄位：`id`, `title`, `summary`, `content`, `category`, `created_at`
- 啟動時自動建表並寫入 seed 假資料

---

### Step 4 — HTMX 搜尋 + 無限捲動

**目標：** 不刷頁搜尋、滾到底自動載入更多新聞。

**新增檔案：**

```
news_net/
├── routers/
│   └── partials.py          # 回傳 HTML 片段的端點
└── templates/
    └── partials/
        └── news_cards.html
```

**技術重點：**

- `hx-trigger="revealed"` 實現無限捲動
- 搜尋框使用 `hx-get="/search" hx-trigger="keyup changed delay:300ms"`
- 後端端點只回傳純 HTML fragment（非完整頁面）

---

### Step 5 — RSS 爬蟲匯入

**目標：** 定期從 RSS 來源抓取新聞並寫入 DB。

**新增檔案：**

```
news_net/
├── scraper/
│   ├── rss_fetcher.py   # 解析 RSS feed
│   └── sources.py       # RSS 來源清單
└── scheduler.py         # APScheduler 定時任務
```

**技術重點：**

- 依賴：`feedparser`、`apscheduler`
- APScheduler 每小時自動抓取一次
- 以 URL hash 去重，避免重複寫入

---

### Step 6 — 分類 / 標籤 / 分頁

**目標：** 新聞可按分類瀏覽，列表有分頁導覽。

**新增內容：**

- `Category` 資料表，與 `Article` 外鍵關聯
- URL 路由 `/category/{slug}` 按分類篩選
- HTMX 分頁片段，點頁碼不刷頁

---

### Step 7 — 管理後台

**目標：** 在後台可新增 / 編輯 / 刪除新聞。

**新增檔案：**

```
news_net/
├── routers/
│   └── admin.py
└── templates/
    └── admin/
        ├── dashboard.html
        └── edit.html
```

**技術重點：**

- HTTP Basic Auth 保護 `/admin` 路由
- HTMX 表單送出後即時顯示操作結果
- 支援文章上下架（草稿 / 已發布狀態）

---

### Step 8 — 快取 + 生產部署

**目標：** 加上快取提升效能，可用 Docker 一鍵部署。

**新增檔案：**

```
news_net/
├── Dockerfile
├── docker-compose.yml
└── .env                 # 環境變數（不納入版控）
```

**技術重點：**

- 依賴：`fastapi-cache2`，搭配 Redis 快取熱門頁面
- Dockerfile 多階段建構，縮小映像大小
- `gunicorn` 搭配 `uvicorn` workers 提升併發能力
- `docker-compose.yml` 同時啟動 app + Redis

---

## 依賴總覽

| 階段 | 新增依賴 |
|------|---------|
| Step 1 | `fastapi` `uvicorn[standard]` `jinja2` |
| Step 2 | `python-multipart` |
| Step 3 | `sqlalchemy` `aiosqlite` |
| Step 4 | （無新依賴，純前端 HTMX CDN） |
| Step 5 | `feedparser` `apscheduler` `httpx` |
| Step 6 | （無新依賴） |
| Step 7 | （無新依賴） |
| Step 8 | `fastapi-cache2` `redis` |

---

## 建議開發順序

1. 完成 Step 1 確認環境可執行
2. Step 2 確認頁面流程正確後再接 DB
3. Step 3 → Step 4 是核心功能，建議完整測試後再繼續
4. Step 5 RSS 爬蟲可獨立測試（直接執行 `rss_fetcher.py`）
5. Step 7 管理後台可依需求決定是否實作
6. Step 8 部署前記得設定 `.env` 環境變數
