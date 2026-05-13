# Build instructions

## Vereisten

- Python 3.11+
- `pip install -r requirements.txt`
- PyInstaller: `pip install pyinstaller`
- Inno Setup 6: https://jrsoftware.org/isinfo.php
- Tesseract-OCR (Windows): https://github.com/UB-Mannheim/tesseract/wiki
  — installeer met talen `nld` (Nederlands) en `eng` (Engels)

## Uitvoerbare bestanden bouwen

Voer de onderstaande commando's uit vanuit de `pdf2md/` map.

### GUI-applicatie

```bat
pyinstaller --onedir --noconsole --name PDF2MD_GUI ^
  --hidden-import fitz --hidden-import fitz.fitz ^
  --collect-all fitz ^
  apps/main_gui.py
```

### Drag & Drop-applicatie

```bat
pyinstaller --onedir --noconsole --name PDF2MD_DragDrop ^
  --hidden-import fitz --hidden-import fitz.fitz ^
  --collect-all fitz ^
  apps/dragdrop.py
```

Na afloop staan de mappen `dist\PDF2MD_GUI\` en `dist\PDF2MD_DragDrop\` klaar.

## Installer compileren

```bat
Iscc.exe installer\setup.iss
```

Dit genereert `Output\PDF2MD_Setup.exe`.

## Mapstructuur na bouwen

```
pdf2md/
├── dist/
│   ├── PDF2MD_GUI/
│   └── PDF2MD_DragDrop/
└── installer/
    └── Output/
        └── PDF2MD_Setup.exe
```

## Opmerkingen

- Zorg dat Tesseract op het doelsysteem geïnstalleerd is in
  `C:\Program Files\Tesseract-OCR\tesseract.exe` (het standaardpad).
  Pas `core/ocr.py` aan als het pad afwijkt.
- De `--onedir`-modus is vereist voor PyMuPDF vanwege de native `.dll`-bestanden.
  De `--onefile`-modus wordt *niet* ondersteund.
