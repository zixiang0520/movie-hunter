"""TMDB API client with proxy support and local caching."""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.parse
from pathlib import Path
from typing import Any, Optional

import httpx

from .models import AppSettings


TMDB_BASE = "https://api.themoviedb.org/3"

if getattr(sys, "frozen", False):
    # EXE mode: use AppData/Local for cache (persistent, not temp)
    _APPDATA = Path(os.environ.get("LOCALAPPDATA", os.path.expanduser("~/.local/share")))
    CACHE_DIR = _APPDATA / "MovieHunter" / "cache"
else:
    CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"


def _cache_path(*parts: str) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    p = CACHE_DIR.joinpath(*parts)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def _load_cache(name: str) -> Optional[dict]:
    p = _cache_path(name + ".json")
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            # Cache TTL: 1 hour
            if time.time() - data.get("_ts", 0) < 3600:
                return data.get("data")
        except Exception:
            pass
    return None


def _save_cache(name: str, data: dict) -> None:
    p = _cache_path(name + ".json")
    p.write_text(
        json.dumps({"_ts": time.time(), "data": data}, ensure_ascii=False),
        encoding="utf-8",
    )


def _get_proxy_from_settings(settings: AppSettings) -> Optional[str]:
    p = settings.proxy
    if p.enabled and p.host:
        return p.url
    # Also check env vars as fallback
    for env_key in ("ALL_PROXY", "HTTPS_PROXY", "HTTP_PROXY"):
        val = os.environ.get(env_key, "").strip()
        if val:
            return val
    return None


class TMDBClient:
    def __init__(self, settings: AppSettings):
        self.settings = settings
        self._client: Optional[httpx.Client] = None

    @property
    def client(self) -> httpx.Client:
        if self._client is None or self._client._settings_key != id(self.settings):
            proxy = _get_proxy_from_settings(self.settings)
            self._client = httpx.Client(
                base_url=TMDB_BASE,
                timeout=30.0,
                proxy=proxy if proxy else None,
                follow_redirects=True,
            )
            self._client._settings_key = id(self.settings)  # type: ignore[attr-defined]
        return self._client

    # ── Helpers ───────────────────────────────────────────────────────

    def _get(self, path: str, params: Optional[dict] = None, cache: bool = True) -> dict:
        """GET request with caching."""
        cache_key = urllib.parse.quote(f"{path}?{urllib.parse.urlencode(params or {})}")
        if cache:
            cached = _load_cache(cache_key)
            if cached is not None:
                return cached

        params = params or {}
        params.setdefault("api_key", self.settings.tmdb_api_key)
        params.setdefault("language", self.settings.language)

        resp = self.client.get(path, params=params)
        resp.raise_for_status()
        data = resp.json()

        if cache:
            _save_cache(cache_key, data)
        return data

    def _get_nocache(self, path: str, params: Optional[dict] = None) -> dict:
        params = params or {}
        params.setdefault("api_key", self.settings.tmdb_api_key)
        params.setdefault("language", self.settings.language)
        resp = self.client.get(path, params=params)
        resp.raise_for_status()
        return resp.json()

    # ── Public API ────────────────────────────────────────────────────

    def search_multi(self, query: str, page: int = 1) -> dict:
        return self._get("/search/multi", {"query": query, "page": page})

    def search_movie(self, query: str, page: int = 1) -> dict:
        return self._get("/search/movie", {"query": query, "page": page})

    def search_tv(self, query: str, page: int = 1) -> dict:
        return self._get("/search/tv", {"query": query, "page": page})

    def search_person(self, query: str, page: int = 1) -> dict:
        return self._get("/search/person", {"query": query, "page": page})

    def get_configuration(self) -> dict:
        return self._get("/configuration")

    def get_movie(self, movie_id: int) -> dict:
        return self._get(f"/movie/{movie_id}")

    def get_movie_credits(self, movie_id: int) -> dict:
        return self._get(f"/movie/{movie_id}/credits")

    def get_movie_similar(self, movie_id: int) -> dict:
        return self._get(f"/movie/{movie_id}/similar")

    def get_movie_images(self, movie_id: int) -> dict:
        return self._get(f"/movie/{movie_id}/images")

    def get_movie_videos(self, movie_id: int) -> dict:
        return self._get(f"/movie/{movie_id}/videos")

    def get_tv(self, tv_id: int) -> dict:
        return self._get(f"/tv/{tv_id}")

    def get_tv_credits(self, tv_id: int) -> dict:
        return self._get(f"/tv/{tv_id}/credits")

    def get_tv_similar(self, tv_id: int) -> dict:
        return self._get(f"/tv/{tv_id}/similar")

    def get_tv_images(self, tv_id: int) -> dict:
        return self._get(f"/tv/{tv_id}/images")

    def get_tv_videos(self, tv_id: int) -> dict:
        return self._get(f"/tv/{tv_id}/videos")

    def get_tv_season(self, tv_id: int, season_number: int) -> dict:
        return self._get(f"/tv/{tv_id}/season/{season_number}")

    def get_person(self, person_id: int) -> dict:
        return self._get(f"/person/{person_id}")

    def get_person_credits(self, person_id: int, credit_type: str = "movie") -> dict:
        return self._get(f"/person/{person_id}/combined_credits")

    def get_genre_list(self, media_type: str = "movie") -> dict:
        return self._get(f"/genre/{media_type}/list")
