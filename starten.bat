@echo off
title PDF2MD
cd /d "%~dp0"

:: ── Controleer Python ─────────────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo Python niet gevonden. Voer eerst installeren.bat uit.
    pause
    exit /b 1
)

:: ── Start de GUI ──────────────────────────────────────────────────────────────
python pdf2md\apps\main_gui.py
