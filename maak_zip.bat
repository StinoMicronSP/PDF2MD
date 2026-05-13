@echo off
title PDF2MD - ZIP maken
cd /d "%~dp0"
echo.
echo  ZIP-bestand wordt aangemaakt voor distributie...
echo.

:: Verwijder oude ZIP als die bestaat
if exist PDF2MD_distributie.zip del PDF2MD_distributie.zip

:: Maak ZIP met PowerShell (ingebouwd in Windows)
powershell -Command "Compress-Archive -Path 'pdf2md', 'installeren.bat', 'starten.bat', 'LEESMIJ.txt' -DestinationPath 'PDF2MD_distributie.zip' -Force"

if errorlevel 1 (
    echo  [FOUT] ZIP aanmaken mislukt.
    pause
    exit /b 1
)

echo.
echo  Klaar! Stuur dit bestand naar je klanten:
echo  PDF2MD_distributie.zip
echo.
echo  Klanten moeten:
echo    1. ZIP uitpakken
echo    2. installeren.bat uitvoeren (eenmalig)
echo    3. starten.bat gebruiken om het programma te starten
echo.
pause
