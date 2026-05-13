@echo off
title PDF2MD - Installer bouwen
cd /d "%~dp0.."
echo.
echo  Installer bouwen (lokaal op Windows)
echo  =====================================
echo.

:: ── Controleer Python ─────────────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo  [FOUT] Python niet gevonden. Installeer Python 3.11+ via python.org
    pause & exit /b 1
)

:: ── Controleer Inno Setup ─────────────────────────────────────────────────────
if not exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    echo  [FOUT] Inno Setup 6 niet gevonden.
    echo  Download via: https://jrsoftware.org/isinfo.php
    pause & exit /b 1
)

:: ── Installeer vereisten ──────────────────────────────────────────────────────
echo  [1/3] Python-pakketten installeren...
pip install --quiet -r requirements.txt pyinstaller

:: ── PyInstaller ───────────────────────────────────────────────────────────────
echo  [2/3] Executables bouwen met PyInstaller...

pyinstaller --onedir --noconsole --name PDF2MD_GUI ^
  --hidden-import fitz --hidden-import fitz.fitz ^
  --collect-all fitz ^
  apps/main_gui.py

pyinstaller --onedir --noconsole --name PDF2MD_DragDrop ^
  --hidden-import fitz --hidden-import fitz.fitz ^
  --collect-all fitz ^
  apps/dragdrop.py

:: ── Inno Setup ────────────────────────────────────────────────────────────────
echo  [3/3] Installer compileren met Inno Setup...
mkdir installer\Output 2>nul
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\setup.iss

echo.
echo  ╔══════════════════════════════════════════╗
echo  ║  Klaar!                                  ║
echo  ║  Installer: installer\Output\PDF2MD_Setup.exe  ║
echo  ╚══════════════════════════════════════════╝
echo.
pause
