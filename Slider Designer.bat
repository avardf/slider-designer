@echo off
setlocal
title Slider Designer
cd /d "%~dp0"

echo.
echo   Slider Designer
echo   ==============================================
echo.

REM ---------- 1. Is uv available? ----------
where uv >nul 2>nul
if errorlevel 1 (
    echo   uv is not installed, or is not on this session's PATH.
    echo.
    echo   Install it by pasting this into PowerShell. It installs into
    echo   your own user profile and does NOT require admin rights:
    echo.
    echo      powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 ^| iex"
    echo.
    echo   If you just installed uv, CLOSE this window and reopen it —
    echo   a new PATH is only picked up by new windows.
    echo.
    pause
    exit /b 1
)

REM ---------- 2. Fetch Python + dependencies ----------
echo   Preparing dependencies (first run downloads ~200 MB, later runs are instant)...
echo.
uv sync
if errorlevel 1 (
    echo.
    echo   ==============================================
    echo   Could not download the dependencies.
    echo.
    echo   On a corporate network this is almost always the proxy or
    echo   TLS inspection blocking the download. Try, in this window:
    echo.
    echo      set HTTP_PROXY=http://your.proxy:port
    echo      set HTTPS_PROXY=http://your.proxy:port
    echo      "%~nx0"
    echo.
    echo   If your company uses TLS inspection, also point uv at the
    echo   corporate root certificate:
    echo.
    echo      set SSL_CERT_FILE=C:\path\to\corporate-root.pem
    echo.
    echo   If your company runs an internal package mirror, use it:
    echo.
    echo      set UV_INDEX_URL=https://your.internal.mirror/simple
    echo.
    echo   Ask IT for the proxy address, the root certificate, or the
    echo   internal PyPI mirror URL — one of those three will fix it.
    echo   ==============================================
    echo.
    pause
    exit /b 1
)

REM ---------- 3. Run ----------
echo.
echo   Starting. Your browser should open automatically.
echo   Leave this window open while you use the app; Ctrl-C stops it.
echo.
REM --server.address=localhost keeps a local run off the network. It lives here
REM rather than in .streamlit\config.toml so cloud deploys still bind 0.0.0.0.
uv run streamlit run app.py --server.address=localhost
if errorlevel 1 (
    echo.
    echo   The app exited with an error — the message above says why.
    echo.
)
pause
