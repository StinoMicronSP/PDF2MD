# Build instructions

## Vereisten

- Python 3.11+
- `pip install -r requirements.txt`
- PyInstaller: `pip install pyinstaller`
- **WiX Toolset v3.11+** (voor MSI): https://wixtoolset.org/releases/
- Tesseract-OCR (Windows): https://github.com/UB-Mannheim/tesseract/wiki
  — installeer met talen `nld` (Nederlands) en `eng` (Engels)

---

## Optie A: Automatisch via GitHub Actions (aanbevolen)

Push een versie-tag en GitHub bouwt de MSI automatisch:

```bat
git tag v1.0.0
git push origin v1.0.0
```

De MSI verschijnt als:
- **Release-artifact** onder *Actions → Build & Release MSI → Artifacts*
- **GitHub Release** op de Releases-pagina (downloadbaar voor eindgebruikers)

Je kunt ook handmatig starten via *Actions → Build & Release MSI → Run workflow*.

---

## Optie B: Lokaal op Windows

### Stap 1 — PyInstaller (vanuit de `pdf2md/` map)

**GUI-applicatie**

```bat
pyinstaller --onedir --noconsole --name PDF2MD_GUI ^
  --hidden-import fitz --hidden-import fitz.fitz ^
  --collect-all fitz ^
  apps/main_gui.py
```

**Drag & Drop-applicatie**

```bat
pyinstaller --onedir --noconsole --name PDF2MD_DragDrop ^
  --hidden-import fitz --hidden-import fitz.fitz ^
  --collect-all fitz ^
  apps/dragdrop.py
```

Na afloop staan `dist\PDF2MD_GUI\` en `dist\PDF2MD_DragDrop\` klaar.

### Stap 2 — MSI bouwen (PowerShell-script)

```powershell
cd pdf2md
.\installer\build_msi.ps1
```

Het script voert automatisch `heat.exe → candle.exe → light.exe` uit.

De MSI verschijnt in: `installer\Output\PDF2MD.msi`

### Stap 2 (alternatief) — Handmatig met WiX-commando's

```bat
:: heat: bestandsoogst
heat.exe dir dist\PDF2MD_GUI ^
  -cg GUI_Files -gg -gl -gd -sfrag -srd ^
  -dr GUI_FOLDER -var var.GuiDir ^
  -out installer\gui_files.wxs

heat.exe dir dist\PDF2MD_DragDrop ^
  -cg DragDrop_Files -gg -gl -gd -sfrag -srd ^
  -dr DRAGDROP_FOLDER -var var.DragDropDir ^
  -out installer\dragdrop_files.wxs

:: candle: compileren
candle.exe -arch x64 ^
  -dGuiDir=dist\PDF2MD_GUI ^
  -dDragDropDir=dist\PDF2MD_DragDrop ^
  -out installer\Output\ ^
  installer\pdf2md.wxs ^
  installer\gui_files.wxs ^
  installer\dragdrop_files.wxs

:: light: linken naar MSI
light.exe ^
  -ext WixUIExtension ^
  -ext WixUtilExtension ^
  -cultures:nl-NL ^
  -out installer\Output\PDF2MD.msi ^
  installer\Output\pdf2md.wixobj ^
  installer\Output\gui_files.wixobj ^
  installer\Output\dragdrop_files.wixobj
```

---

## Mapstructuur na bouwen

```
pdf2md/
├── dist/
│   ├── PDF2MD_GUI/
│   └── PDF2MD_DragDrop/
└── installer/
    ├── gui_files.wxs        ← gegenereerd door heat.exe
    ├── dragdrop_files.wxs   ← gegenereerd door heat.exe
    └── Output/
        └── PDF2MD.msi       ← eindresultaat
```

---

## Nieuwe versie uitbrengen

1. Pas `Version="x.y.z"` aan in `installer/pdf2md.wxs`
2. Commit en tag:
   ```bat
   git add installer/pdf2md.wxs
   git commit -m "Bump version to x.y.z"
   git tag vx.y.z
   git push origin main --tags
   ```
3. GitHub Actions bouwt de MSI automatisch en maakt een Release aan.

---

## Opmerkingen

- Zorg dat Tesseract op het doelsysteem geïnstalleerd is in
  `C:\Program Files\Tesseract-OCR\tesseract.exe` (het standaardpad).
  Pas `core/ocr.py` aan als het pad afwijkt.
- De `--onedir`-modus is **vereist** voor PyMuPDF vanwege de native `.dll`-bestanden.
  De `--onefile`-modus wordt *niet* ondersteund.
- De `UpgradeCode` in `pdf2md.wxs` mag **nooit** worden gewijzigd;
  alleen de `ProductCode` verandert bij major releases.
