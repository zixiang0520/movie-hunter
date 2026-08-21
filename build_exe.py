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
    pyinstaller_args = [
        "--onefile",                     # 单文件 EXE
        "--windowed",                     # 无控制台窗口（pywebview 弹窗）
        "--name=MovieHunter",             # 输出文件名
        "--noconsole",                    # 同 --windowed
        "--hidden-import=backend.main",   # 隐藏导入
        "--hidden-import=backend.models",
        "--hidden-import=backend.service",
        "--hidden-import=backend.settings",
        "--hidden-import=backend.tmdb_client",
        "--collect-all=httpx",            # 收集 httpx 全部资源
        "--collect-all=fastapi",
        "--collect-all=pydantic",
        "--collect-all=uvicorn",
        "--collect-all=starlette",
        "--collect-all=anyio",
        "--collect-all=snowflake_id",
        "--copy-metadata=pywebview",      # 复制 pywebview 元数据
        "--copy-metadata=fastapi",
        "--copy-metadata=httpx",
        "--copy-metadata=uvicorn",
        "--copy-metadata=pydantic",
        "--copy-metadata=starlette",
        "--paths=" + str(HERE),            # 项目根路径
        str(HERE / "desktop.py"),          # 入口文件
    ]

    print(f"  📦  构建参数:")
    for arg in pyinstaller_args:
        if arg.startswith("--"):
            print(f"      {arg}")
        elif arg == str(HERE / "desktop.py"):
            print(f"      📄  入口: desktop.py")

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