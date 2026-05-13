<#
.SYNOPSIS
    Bouwt de PDF2MD MSI-installer lokaal op een Windows-machine.

.DESCRIPTION
    Stappen:
    1. PyInstaller — bouw GUI en DragDrop executables
    2. WiX heat.exe — oogst alle bestanden uit de dist-mappen
    3. WiX candle.exe — compileer alle .wxs-bestanden naar .wixobj
    4. WiX light.exe — link naar één .msi

.REQUIREMENTS
    - Python 3.11+ in PATH
    - PyInstaller: pip install pyinstaller
    - WiX Toolset v3.11+: https://wixtoolset.org/releases/
      Zorg dat %WIX%\bin in PATH staat, of pas $WixBin hieronder aan.

.EXAMPLE
    cd pdf2md
    .\installer\build_msi.ps1
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ── Configuratie ──────────────────────────────────────────────────────────────
$WixBin   = if ($env:WIX) { "$env:WIX\bin" } else { "C:\Program Files (x86)\WiX Toolset v3.11\bin" }
$Root     = Split-Path $PSScriptRoot -Parent   # pdf2md/ map
$Dist     = Join-Path $Root "dist"
$Inst     = $PSScriptRoot                       # pdf2md/installer/
$Out      = Join-Path $Inst "Output"

# ── Hulpfunctie ──────────────────────────────────────────────────────────────
function Step([string]$msg) {
    Write-Host "`n==> $msg" -ForegroundColor Cyan
}

# ── 1. PyInstaller ────────────────────────────────────────────────────────────
Step "PyInstaller: GUI"
Push-Location $Root
pyinstaller --onedir --noconsole --name PDF2MD_GUI `
    --hidden-import fitz --hidden-import fitz.fitz `
    --collect-all fitz `
    apps/main_gui.py

Step "PyInstaller: DragDrop"
pyinstaller --onedir --noconsole --name PDF2MD_DragDrop `
    --hidden-import fitz --hidden-import fitz.fitz `
    --collect-all fitz `
    apps/dragdrop.py
Pop-Location

# ── 2. heat.exe — bestandsoogst ───────────────────────────────────────────────
$Heat = Join-Path $WixBin "heat.exe"

Step "heat.exe: GUI-bestanden"
& $Heat dir "$Dist\PDF2MD_GUI" `
    -cg GUI_Files `
    -gg -gl -gd -sfrag -srd `
    -dr GUI_FOLDER `
    -var var.GuiDir `
    -out "$Inst\gui_files.wxs"

Step "heat.exe: DragDrop-bestanden"
& $Heat dir "$Dist\PDF2MD_DragDrop" `
    -cg DragDrop_Files `
    -gg -gl -gd -sfrag -srd `
    -dr DRAGDROP_FOLDER `
    -var var.DragDropDir `
    -out "$Inst\dragdrop_files.wxs"

# ── 3. candle.exe — compileren ────────────────────────────────────────────────
$Candle = Join-Path $WixBin "candle.exe"
New-Item -ItemType Directory -Force $Out | Out-Null

Step "candle.exe"
& $Candle `
    -arch x64 `
    "-dGuiDir=$Dist\PDF2MD_GUI" `
    "-dDragDropDir=$Dist\PDF2MD_DragDrop" `
    -out "$Out\" `
    "$Inst\pdf2md.wxs" `
    "$Inst\gui_files.wxs" `
    "$Inst\dragdrop_files.wxs"

# ── 4. light.exe — linken ─────────────────────────────────────────────────────
$Light = Join-Path $WixBin "light.exe"

Step "light.exe"
& $Light `
    -ext WixUIExtension `
    -ext WixUtilExtension `
    -cultures:nl-NL `
    -out "$Out\PDF2MD.msi" `
    "$Out\pdf2md.wixobj" `
    "$Out\gui_files.wixobj" `
    "$Out\dragdrop_files.wixobj"

Step "Klaar!"
Write-Host "MSI aangemaakt: $Out\PDF2MD.msi" -ForegroundColor Green
