@echo off
title PDF2MD - Installatie
color 0A
echo.
echo  ╔══════════════════════════════════════╗
echo  ║     PDF2MD - Eerste installatie      ║
echo  ╚══════════════════════════════════════╝
echo.

:: ── Controleer of Python aanwezig is ─────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo  [FOUT] Python is niet geinstalleerd.
    echo.
    echo  Installeer Python via:
    echo  https://www.python.org/downloads/
    echo.
    echo  Vink tijdens installatie aan:
    echo    [x] Add Python to PATH
    echo.
    pause
    start https://www.python.org/downloads/
    exit /b 1
)

echo  [OK] Python gevonden.
echo.
echo  Benodigde programma's worden geinstalleerd...
echo  (dit duurt 1-2 minuten, even geduld)
echo.

:: ── Installeer vereiste pakketten ─────────────────────────────────────────────
pip install --quiet --upgrade pip
pip install --quiet PyMuPDF>=1.23 pytesseract>=0.3.10 Pillow>=10.0 pandas>=2.0 openpyxl>=3.1 rapidfuzz>=3.0

if errorlevel 1 (
    echo.
    echo  [FOUT] Installatie mislukt.
    echo  Controleer je internetverbinding en probeer opnieuw.
    pause
    exit /b 1
)

echo.
echo  ╔══════════════════════════════════════╗
echo  ║     Installatie geslaagd!            ║
echo  ║     Gebruik starten.bat om te starten║
echo  ╚══════════════════════════════════════╝
echo.
echo  TIP: Tesseract-OCR is optioneel (alleen nodig voor gescande PDF's).
echo  Download via: https://github.com/UB-Mannheim/tesseract/wiki
echo.
pause
