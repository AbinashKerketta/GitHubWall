@echo off
title GitHubWall - Generate Stats
cd /d "%~dp0"
echo ===========================================
echo   GitHubWall - Generate README Stats
echo ===========================================
echo.
python generate.py --username AbinashKerketta --theme dark
echo.
if %errorlevel% neq 0 (
    echo [!] Generation failed. Check Python is installed and in PATH.
) else (
    echo [+] Done! Check the output\ folder for your SVGs.
)
echo.
echo [DONE] Press any key to exit.
pause >nul
