"""Movie Hunter — Windows EXE 打包脚本（PyInstaller）。

使用方法（Windows）：
    pip install pyinstaller
    python build_exe.py

输出: dist/MovieHunter.exe（双击即可运行，无需 Python 环境）
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

# Fix Windows console encoding (cp1252 can't handle emoji/unicode)
if sys.stdout.encoding and "cp" in sys.stdout.encoding.lower():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent


def main() -> None:
    print("\n[Movie Hunter] EXE building...\n")

    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("[ERROR] Please install PyInstaller first:")
        print("  pip install pyinstaller\n")
        sys.exit(1)

    for d in ("build", "dist"):
        p = HERE / d
        if p.exists():
            shutil.rmtree(p)
            print(f"[CLEAN] Removed: {p}")

    # Use os.pathsep for --add-data separator (":" on Linux, ";" on Windows)
    pyinstaller_args = [
        "--onefile",
        "--windowed",
        "--noconsole",
        "--name=MovieHunter",
        # Include web/, config/, backend/ as data files (extracted at runtime)
        f"--add-data={HERE / 'web'}{os.pathsep}web",
        f"--add-data={HERE / 'backend'}{os.pathsep}backend",
        # Backend modules
        "--hidden-import=backend.main",
        "--hidden-import=backend.models",
        "--hidden-import=backend.service",
        "--hidden-import=backend.settings",
        "--hidden-import=backend.tmdb_client",
        "--hidden-import=backend",
        # FastAPI stack
        "--hidden-import=fastapi",
        "--hidden-import=fastapi.middleware.cors",
        "--hidden-import=fastapi.responses",
        "--hidden-import=fastapi.staticfiles",
        "--hidden-import=starlette",
        "--hidden-import=starlette.middleware",
        "--hidden-import=starlette.routing",
        "--hidden-import=starlette.staticfiles",
        "--hidden-import=uvicorn",
        "--hidden-import=uvicorn.main",
        "--hidden-import=uvicorn.logging",
        "--hidden-import=uvicorn.lifespan.on",
        "--hidden-import=uvicorn.protocols.http.h11_impl",
        "--hidden-import=uvicorn.protocols.http.httptools_impl",
        "--hidden-import=uvicorn.protocols.websockets.websockets_impl",
        "--hidden-import=uvicorn.protocols.websockets.wsproto_impl",
        "--hidden-import=uvicorn.loops.auto",
        "--hidden-import=httptools",
        "--hidden-import=websockets",
        "--hidden-import=wsproto",
        "--hidden-import=pydantic",
        "--hidden-import=pydantic_settings",
        "--hidden-import=httpx",
        "--hidden-import=httpcore",
        "--hidden-import=h11",
        "--hidden-import=sniffio",
        "--hidden-import=anyio",
        "--hidden-import=anyio.from_thread",
        "--hidden-import=anyio._backends._asyncio",
        "--hidden-import=watchfiles",
        "--hidden-import=soupsieve",
        # Desktop
        "--hidden-import=webview",
        # OpenSSL
        "--hidden-import=crypto",
        "--hidden-import=cryptography",
        "--hidden-import=cryptography.hazmat",
        "--hidden-import=cryptography.x509",
        "--hidden-import=cryptography.hazmat.primitives",
        "--hidden-import=cffi",
        # Metadata
        "--copy-metadata=pywebview",
        "--copy-metadata=fastapi",
        "--copy-metadata=httpx",
        "--copy-metadata=uvicorn",
        "--copy-metadata=pydantic",
        "--paths=" + str(HERE),
        str(HERE / "desktop.py"),
    ]

    print(f"[CONFIG] Entry: desktop.py")
    print(f"[CONFIG] Args: onefile + windowed + {len(pyinstaller_args)} hidden imports")

    from PyInstaller.__main__ import run as pyinstaller_run

    print("\n[BUILD] Starting PyInstaller (1-3 minutes)...\n")
    pyinstaller_run(pyinstaller_args)

    exe_path = HERE / "dist" / "MovieHunter.exe"
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"\n[OK] Build successful!")
        print(f"     File: {exe_path}")
        print(f"     Size: {size_mb:.1f} MB")
        print(f"\n     Double-click MovieHunter.exe to run")
    else:
        print(f"\n[ERROR] Output not found: {exe_path}")
        sys.exit(1)


if __name__ == "__main__":
    main()