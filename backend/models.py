"""Pydantic models for TMDB data and app settings."""
from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field


# ── Settings ──────────────────────────────────────────────────────────

class ProxyConfig(BaseModel):
    enabled: bool = False
    protocol: str = "http"        # http | https | socks5 | socks5h
    host: str = ""
    port: int = 0
    username: str = ""
    password: str = ""

    @property
    def url(self) -> str:
        if not self.enabled or not self.host:
            return ""
        auth = f"{self.username}:{self.password}@" if self.username else ""
        return f"{self.protocol}://{auth}{self.host}:{self.port}"

    @classmethod
    def from_full_url(cls, url: str) -> "ProxyConfig":
        """Parse a full proxy URL like http://user:pass@host:port or socks5://host:port."""
        import re
        m = re.match(
            r"(?P<proto>https?|socks5h?|socks4?)://(?:(?P<user>[^:]+):(?P<pass>[^@]*)@)?(?P<host>[^:]+):(?P<port>\d+)",
            url,
        )
        if m:
            d = m.groupdict()
            return cls(
                enabled=True,
                protocol=d["proto"],
                host=d["host"],
                port=int(d["port"]),
                username=d.get("user") or "",
                password=d.get("pass") or "",
            )
        return cls(enabled=False)


class AppSettings(BaseModel):
    tmdb_api_key: str = ""
    language: str = "zh-CN"
    proxy: ProxyConfig = ProxyConfig()
    admin_password_hash: str = ""  # PBKDF2 hash of admin password

    def to_dict(self) -> dict:
        return self.model_dump()

    @classmethod
    def from_dict(cls, d: dict) -> "AppSettings":
        if "proxy" in d and isinstance(d["proxy"], dict):
            d["proxy"] = ProxyConfig(**d["proxy"])
        return cls(**d)


# ── TMDB Models ───────────────────────────────────────────────────────

class CrewMember(BaseModel):
    id: int = 0
    name: str = ""
    job: str = ""
    department: str = ""
    profile_path: Optional[str] = None


class CastMember(BaseModel):
    id: int = 0
    name: str = ""
    character: str = ""
    profile_path: Optional[str] = None
    order: int = 0


class Genre(BaseModel):
    id: int = 0
    name: str = ""


class ProductionCompany(BaseModel):
    id: int = 0
    name: str = ""
    logo_path: Optional[str] = None
    origin_country: str = ""


class ProductionCountry(BaseModel):
    iso_3166_1: str = ""
    name: str = ""


class SpokenLanguage(BaseModel):
    english_name: str = ""
    name: str = ""
    iso_639_1: str = ""


class PersonDetails(BaseModel):
    id: int = 0
    name: str = ""
    biography: str = ""
    profile_path: Optional[str] = None
    birthday: Optional[str] = None
    known_for_department: str = ""
    also_known_as: list[str] = Field(default_factory=list)
    popularity: float = 0.0
    gender: int = 0
    deathday: Optional[str] = None
    place_of_birth: Optional[str] = None


class MovieDetail(BaseModel):
    id: int = 0
    title: str = ""
    overview: str = ""
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    release_date: str = ""
    runtime: int = 0
    vote_average: float = 0.0
    vote_count: int = 0
    popularity: float = 0.0
    tagline: str = ""
    genres: list[Genre] = Field(default_factory=list)
    production_companies: list[ProductionCompany] = Field(default_factory=list)
    production_countries: list[ProductionCountry] = Field(default_factory=list)
    spoken_languages: list[SpokenLanguage] = Field(default_factory=list)
    status: str = ""
    budget: int = 0
    revenue: int = 0
    original_language: str = ""
    original_title: str = ""
    cast: list[CastMember] = Field(default_factory=list)
    crew: list[CrewMember] = Field(default_factory=list)
    similar: list[dict] = Field(default_factory=list)


class SeasonDetail(BaseModel):
    id: int = 0
    name: str = ""
    overview: str = ""
    poster_path: Optional[str] = None
    air_date: str = ""
    episode_count: int = 0
    episodes: list[dict] = Field(default_factory=list)


class TVDetail(BaseModel):
    id: int = 0
    name: str = ""
    overview: str = ""
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    first_air_date: str = ""
    vote_average: float = 0.0
    vote_count: int = 0
    popularity: float = 0.0
    genres: list[Genre] = Field(default_factory=list)
    production_companies: list[ProductionCompany] = Field(default_factory=list)
    production_countries: list[ProductionCountry] = Field(default_factory=list)
    spoken_languages: list[SpokenLanguage] = Field(default_factory=list)
    status: str = ""
    original_language: str = ""
    original_name: str = ""
    episode_run_time: list[int] = Field(default_factory=list)
    number_of_seasons: int = 0
    number_of_episodes: int = 0
    seasons: list[dict] = Field(default_factory=list)
    cast: list[CastMember] = Field(default_factory=list)
    crew: list[CrewMember] = Field(default_factory=list)
    seasons_detail: list[SeasonDetail] = Field(default_factory=list)
    similar: list[dict] = Field(default_factory=list)


class PersonItem(BaseModel):
    id: int = 0
    name: str = ""
    known_for_department: str = ""
    profile_path: Optional[str] = None
    popularity: float = 0.0
    known_for: list[dict] = Field(default_factory=list)
