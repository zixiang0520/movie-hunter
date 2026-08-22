"""Movie Hunter — Windows EXE 打包脚本（PyInstaller）。

使用方法（Windows）：
    pip install pyinstaller
    python build_exe.py

输出: dist/MovieHunter.exe（双击即可运行，无需 Python 环境）
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> None:
    print("\n🎬  Movie Hunter EXE 打包中...\n")

    # ── Check PyInstaller ────────────────────────────────────────────
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("❌ 请先安装 PyInstaller:")
        print("   pip install pyinstaller\n")
        sys.exit(1)

    # ── Clean previous build ─────────────────────────────────────────
    for d in ("build", "dist"):
        p = HERE / d
        if p.exists():
            shutil.rmtree(p)
            print(f"  🗑️  清理旧目录: {p}")

    # ── PyInstaller options ──────────────────────────────────────────
    # 注意：使用 --hidden-import 逐个声明依赖，比 --collect-all 更可靠
    #       因为 --collect-all 需要包已安装且可导入
    pyinstaller_args = [
        "--onefile",
        "--windowed",
        "--noconsole",
        "--name=MovieHunter",
        # 隐藏导入（确保所有模块都被打包）
        "--hidden-import=backend.main",
        "--hidden-import=backend.models",
        "--hidden-import=backend.service",
        "--hidden-import=backend.settings",
        "--hidden-import=backend.tmdb_client",
        "--hidden-import=backend",
        # FastAPI 依赖树
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
        "--hidden-import=webview",
        # OpenSSL（httpx 需要）
        "--hidden-import=crypto",
        "--hidden-import=cryptography",
        "--hidden-import=cryptography.hazmat",
        "--hidden-import=cryptography.x509",
        "--hidden-import=cryptography.hazmat.primitives",
        "--hidden-import=cffi",
        # PyInstaller hooks
        "--copy-metadata=pywebview",
        "--copy-metadata=fastapi",
        "--copy-metadata=httpx",
        "--copy-metadata=uvicorn",
        "--copy-metadata=pydantic",
        "--paths=" + str(HERE),
        str(HERE / "desktop.py"),
    ]

    print(f"  📦  入口: desktop.py")
    print(f"  📦  参数: 1 文件模式 + 无控制台 + {len(pyinstaller_args)} 项配置")

    # ── Run PyInstaller ─────────────────────────────────────────────
    from PyInstaller.__main__ import run as pyinstaller_run

    print("\n  ⏳  正在构建（约需 1-3 分钟）...\n")
    pyinstaller_run(pyinstaller_args)

    # ── Verify output ───────────────────────────────────────────────
    exe_path = HERE / "dist" / "MovieHunter.exe"
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"\n✅  打包成功！")
        print(f"   📁  {exe_path}")
        print(f"   📏  {size_mb:.1f} MB")
        print(f"\n   双击 MovieHunter.exe 即可运行 🎬")
    else:
        print(f"\n❌  未找到输出文件: {exe_path}")
        sys.exit(1)


if __name__ == "__main__":
    main()