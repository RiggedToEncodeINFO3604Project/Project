"""
app/main.py
───────────
FastAPI application — stateless, Render-ready.

Direct port of  src/server.js.

Route map (identical paths to the JS version so the frontend needs
zero changes):
    GET  /api/health   →  liveness probe (Render healthCheckPath)
    POST /api/chat     →  { message, history } → { answer, matchedSections }
    GET  /*            →  serve index.html (SPA catch-all)

GITHUB PATH  →  app/main.py
"""

import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .gemini_client import chat

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(name)s  %(message)s")
log = logging.getLogger("skedulelt.server")

# ── Paths ────────────────────────────────────────────────────────────────────
# static/ lives one level up from this file's parent (app/)
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

# ── FastAPI app ──────────────────────────────────────────────────────────────
app = FastAPI(title="Skedulelt RAG", docs_url="/docs", redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # fine for dev; restrict in prod
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount /static so that CSS / images can be served if added later.
# We do NOT mount on "/" yet — that would swallow the catch-all below.
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# ── Pydantic schemas ─────────────────────────────────────────────────────────

class HistoryTurn(BaseModel):
    role: str   # "user" | "assistant"
    text: str


class ChatRequest(BaseModel):
    message: str
    history: list[HistoryTurn] = []


class ChatResponse(BaseModel):
    answer:           str
    matchedSections:  list[str]    # camelCase kept intentional — matches JS payload


# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {
        "status":   "ok",
        "model":    "gemini-1.5-flash",
        "approach": "long-context-stateless",
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(body: ChatRequest):
    """
    Stateless chat endpoint.  The browser sends the full conversation
    history; the server rebuilds the prompt and forwards to Gemini.
    """
    # Convert Pydantic models → plain dicts for gemini_client
    history_dicts = [{"role": t.role, "text": t.text} for t in body.history]

    result = await chat(history_dicts, body.message)

    return ChatResponse(
        answer=result.answer,
        matchedSections=result.matched_sections,
    )


# ── SPA catch-all (must be last) ─────────────────────────────────────────────
# Any GET that didn't match /api/* or /static/* returns index.html.

_INDEX_HTML: str | None = None


def _read_index() -> str:
    global _INDEX_HTML
    if _INDEX_HTML is None:
        _INDEX_HTML = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
    return _INDEX_HTML


@app.get("/{full_path:path}")
async def spa_fallback(full_path: str):
    return HTMLResponse(content=_read_index())
