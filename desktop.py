"""Movie Hunter — Windows Desktop Launcher (pywebview)."""
from __future__ import annotations

import os
import sys
import threading
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if getattr(sys, "frozen", False):
    MEIPASS = Path(sys._MEIPASS)
else:
    MEIPASS = PROJECT_ROOT
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    import webview
except ImportError:
    print("请先安装 pywebview: pip install pywebview")
    sys.exit(1)

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.main import app


def run_server():
    """Run the FastAPI server in a background thread."""
    import uvicorn
    os.environ.setdefault("MH_HOST", "127.0.0.1")
    os.environ.setdefault("MH_PORT", "8766")
    uvicorn.run(app, host=os.environ["MH_HOST"], port=int(os.environ["MH_PORT"]), log_level="warning")


def main():
    port = int(os.environ.get("MH_PORT", "8766"))
    url = f"http://127.0.0.1:{port}"

    # Start the server in a background thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    webview.create_window(
        "🎬 Movie Hunter — 影视猎手",
        url,
        width=1280,
        height=820,
        min_size=(800, 600),
        resizable=True,
        focus=True,
    )
    webview.start()


if __name__ == "__main__":
    main()
