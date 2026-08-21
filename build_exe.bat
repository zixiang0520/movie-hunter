@echo off
REM Movie Hunter — Windows EXE 打包快捷脚本
REM 用法: 双击 build_exe.bat 或命令行运行

echo.
echo. ╔══════════════════════════════════════════════╗
echo   ║   🎬  Movie Hunter EXE 打包               ║
echo   ╚══════════════════════════════════════════════╝
echo.

REM 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌  未找到 Python，请先安装 Python 3.11+
    pause
    exit /b 1
)

REM 检查 PyInstaller
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo ⏳  正在安装 PyInstaller...
    pip install pyinstaller
    if %errorlevel% neq 0 (
        echo ❌  安装失败
        pause
        exit /b 1
    )
)

echo 📦  开始打包...
echo.
python build_exe.py

if %errorlevel% neq 0 (
    echo.
    echo ❌  打包失败
) else (
    echo.
    echo ✅  完成！打开 dist\ 文件夹找到 MovieHunter.exe
)

echo.
pause