from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI(title="全球新聞網 API (簡略版)")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ── 模擬新聞資料 ──────────────────────────────────────────────
MOCK_NEWS = [
    {"id": 1, "title": "全球 AI 晶片趨勢", "category": "Tech"},
    {"id": 2, "title": "Fed 利率決策出爐", "category": "Finance"},
    {"id": 3, "title": "巴黎奧運最新戰報", "category": "Sports"},
]


# ── Pydantic 模型 ─────────────────────────────────────────────
class TranslationRequest(BaseModel):
    text: str
    target_lang: str


# ── 前端路由 ──────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


# ── API 路由 ──────────────────────────────────────────────────
@app.get("/api/news")
def get_news_list():
    """獲取新聞列表"""
    return MOCK_NEWS


@app.get("/api/news/{news_id}")
def get_news_detail(news_id: int):
    """獲取新聞內文"""
    return {"id": news_id, "title": "新聞標題", "content": "詳細內文..."}


@app.post("/api/translate")
def translate_news(request: TranslationRequest):
    """AI 多語系翻譯與摘要"""
    return {
        "translated_text": f"[AI 翻譯-{request.target_lang}]: 處理完成",
        "ai_summary": "這是 AI 生成的摘要內容。",
    }
