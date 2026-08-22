"""Settings persistence — reads/writes config/settings.json."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from .models import AppSettings

if getattr(sys, "frozen", False):
    _APPDATA = Path(os.environ.get("LOCALAPPDATA", os.path.expanduser("~/.local/share")))
    _BASE = _APPDATA / "MovieHunter"
else:
    _BASE = Path(__file__).resolve().parent.parent

_BASE.mkdir(parents=True, exist_ok=True)
SETTINGS_FILE = _BASE / "config" / "settings.json"

_DEFAULT = AppSettings()


def load_settings() -> AppSettings:
    if SETTINGS_FILE.exists():
        try:
            d = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
            return AppSettings.from_dict(d)
        except Exception:
            return _DEFAULT
    return _DEFAULT


def save_settings(settings: AppSettings) -> None:
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(
        json.dumps(settings.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
