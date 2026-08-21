"""Movie Hunter — FastAPI web server (web version backend)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure project root is on sys.path so sibling imports work
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles

from backend.models import AppSettings, ProxyConfig
from backend.service import fetch_movie_detail, fetch_person_detail, fetch_tv_detail
from backend.settings import load_settings, save_settings
from backend.tmdb_client import TMDBClient


BASE_DIR = Path(__file__).resolve().parent.parent
WEB_DIR = BASE_DIR / "web"


def _ensure_default_settings():
    """Create a default settings file if it doesn't exist."""
    settings = load_settings()
    if not settings.tmdb_api_key:
        save_settings(settings)


# ── App lifecycle ─────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    _ensure_default_settings()
    yield


app = FastAPI(
    title="Movie Hunter",
    description="影视资料查询工具 — 基于 TMDB API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files last (but before the catch-all route)
app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")


# ── Image proxy ────────────────────────────────────────────────────

TMDB_IMG_BASE = "https://image.tmdb.org/t/p/"


@app.get("/api/image/{size}/{path:path}")
async def api_image(size: str, path: str):
    """Proxy TMDB images through the backend (bypasses GFW for the browser)."""
    import mimetypes
    import httpx

    settings = load_settings()
    proxy_url = None
    if settings.proxy.enabled:
        protocol = settings.proxy.protocol
        auth = ""
        if settings.proxy.username:
            auth = f"{settings.proxy.username}:{settings.proxy.password}@"
        proxy_url = f"{protocol}://{auth}{settings.proxy.host}:{settings.proxy.port}"

    img_url = f"{TMDB_IMG_BASE}{size}/{path}"
    ext = path.rsplit(".", 1)[-1].lower() if "." in path else "jpg"
    mime_map = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}
    media_type = mime_map.get(ext, "image/jpeg")

    try:
        client = httpx.Client(proxy=proxy_url, timeout=30.0)
        resp = client.get(img_url, headers={"User-Agent": "Mozilla/5.0"})
        client.close()
        return Response(
            content=resp.content,
            media_type=media_type,
            headers={"Cache-Control": "max-age=86400"},
        )
    except Exception:
        raise HTTPException(502, "图片获取失败")


# ── Utility ───────────────────────────────────────────────────────────

def _get_client() -> TMDBClient:
    settings = load_settings()
    if not settings.tmdb_api_key:
        raise HTTPException(400, "请先在设置页面配置 TMDB API Key")
    return TMDBClient(settings)


# ── Settings API ──────────────────────────────────────────────────────

@app.get("/api/settings")
def api_get_settings():
    settings = load_settings()
    d = settings.to_dict()
    d.pop("admin_password_hash", None)  # Don't leak hash to client
    d["has_password"] = bool(settings.admin_password_hash)
    return d


@app.post("/api/settings")
def api_save_settings(data: dict, admin_password: str = Query("", min_length=0)):
    """Save settings. admin_password is required if a password is already set."""
    import hashlib
    import os

    current = load_settings()
    stored_hash = current.admin_password_hash

    if stored_hash:
        # Verify password
        parts = stored_hash.split(":")
        if len(parts) != 2:
            raise HTTPException(401, "密码验证失败")
        salt, expected = parts
        computed = hashlib.pbkdf2_hmac(
            "sha256", admin_password.encode("utf-8"), salt.encode("utf-8"), 100000
        ).hex()
        if computed != expected:
            raise HTTPException(401, "密码错误，请重试")

    # Also allow password change via this endpoint
    new_password = data.pop("_set_password", None)
    settings = AppSettings.from_dict(data)

    # If setting a new password or changing it
    if new_password is not None and new_password != "":
        salt = os.urandom(16).hex()
        digest = hashlib.pbkdf2_hmac(
            "sha256", new_password.encode("utf-8"), salt.encode("utf-8"), 100000
        ).hex()
        settings.admin_password_hash = f"{salt}:{digest}"
    elif new_password == "":
        # Clear password
        settings.admin_password_hash = ""
    else:
        # Keep existing hash
        settings.admin_password_hash = stored_hash

    save_settings(settings)
    return {"ok": True}


@app.get("/api/settings/check-password")
def api_check_password(admin_password: str = Query("", min_length=0)):
    """Check if admin password is correct. Returns {ok: bool, has_password: bool}."""
    import hashlib

    current = load_settings()
    stored_hash = current.admin_password_hash
    if not stored_hash:
        return {"ok": False, "has_password": False}

    parts = stored_hash.split(":")
    if len(parts) != 2:
        return {"ok": False, "has_password": True}
    salt, expected = parts
    computed = hashlib.pbkdf2_hmac(
        "sha256", admin_password.encode("utf-8"), salt.encode("utf-8"), 100000
    ).hex()
    return {"ok": computed == expected, "has_password": True}


# ── TMDB API endpoints ────────────────────────────────────────────────

@app.get("/api/config")
def api_tmdb_config():
    client = _get_client()
    return client.get_configuration()


@app.get("/api/search")
def api_search(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
):
    client = _get_client()
    return client.search_multi(q, page)


@app.get("/api/movie/{movie_id}")
def api_movie(movie_id: int):
    client = _get_client()
    detail = fetch_movie_detail(client, movie_id)
    images = client.get_movie_images(movie_id)
    videos = client.get_movie_videos(movie_id)
    return {
        "detail": detail.model_dump(),
        "images": images.get("posters", []) + images.get("backdrops", []),
        "videos": videos.get("results", []),
    }


@app.get("/api/tv/{tv_id}")
def api_tv(tv_id: int, season: Optional[int] = None):
    client = _get_client()
    detail = fetch_tv_detail(client, tv_id)

    seasons_detail = []
    if season is not None:
        sd = client.get_tv_season(tv_id, season)
        seasons_detail.append(sd)
    elif detail.number_of_seasons > 0:
        # Fetch season 1 by default
        try:
            sd = client.get_tv_season(tv_id, 1)
            seasons_detail.append(sd)
        except Exception:
            pass

    images = client.get_tv_images(tv_id)
    videos = client.get_tv_videos(tv_id)
    return {
        "detail": detail.model_dump(),
        "seasons_detail": [s for s in seasons_detail],
        "images": images.get("posters", []) + images.get("backdrops", []),
        "videos": videos.get("results", []),
    }


@app.get("/api/person/{person_id}")
def api_person(person_id: int):
    client = _get_client()
    detail = fetch_person_detail(client, person_id)
    credits = client.get_person_credits(person_id, "movie")
    return {
        "detail": detail.model_dump(),
        "movie_credits": credits.get("cast", [])[:20],
    }


# ── Serve web UI ──────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def index():
    return FileResponse(str(WEB_DIR / "index.html"))


@app.get("/{path:path}", response_class=HTMLResponse)
def spa_fallback(path: str):
    """Return index.html for any unmatched route (SPA fallback)."""
    fp = WEB_DIR / path
    if fp.exists():
        return FileResponse(str(fp))
    return FileResponse(str(WEB_DIR / "index.html"))


# ── CLI entry ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    host = os.environ.get("MH_HOST", "0.0.0.0")
    port = int(os.environ.get("MH_PORT", "8765"))
    print(f"\n🎬  Movie Hunter 启动中...")
    print(f"   网页地址: http://localhost:{port}")
    print(f"   按 Ctrl+C 停止\n")
    uvicorn.run("backend.main:app", host=host, port=port, reload=False)
