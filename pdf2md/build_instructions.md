# Build instructions

## Vereisten

- Python 3.11+
- `pip install -r requirements.txt`
- PyInstaller: `pip install pyinstaller`
- **Inno Setup 6**: https://jrsoftware.org/isinfo.php
- Tesseract-OCR (optioneel, voor gescande PDF's): https://github.com/UB-Mannheim/tesseract/wiki
  — installeer met talen `nld` (Nederlands) en `eng` (Engels)

---

## Optie A: Automatisch via GitHub Actions (aanbevolen)

Push een versie-tag en GitHub bouwt de installer automatisch:

```bat
git tag v1.0.0
git push origin v1.0.0
```

De installer verschijnt als:
- **Release-artifact** onder *Actions → Build & Release Installer → Artifacts*
- **GitHub Release** op de Releases-pagina (downloadbaar voor eindgebruikers)

Je kunt ook handmatig starten via *Actions → Build & Release Installer → Run workflow*.

---

## Optie B: Lokaal op Windows

### Stap 1 — PyInstaller (vanuit de `pdf2md/` map)

**GUI-applicatie** (inclusief tkinterdnd2 voor drag & drop)

```bat
pyinstaller --onedir --noconsole --name PDF2MD_GUI ^
  --hidden-import fitz --hidden-import fitz.fitz ^
  --hidden-import tkinterdnd2 ^
  --collect-all fitz ^
  --collect-all tkinterdnd2 ^
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

### Stap 2 — Installer bouwen

```bat
installer\build_local.bat
```

Of rechtstreeks:

```bat
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\setup.iss
```

Resultaat: `installer\Output\PDF2MD_Setup.exe`

---

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

---

## Nieuwe versie uitbrengen

```bat
git commit -m "Bump version to x.y.z"
git tag vx.y.z
git push origin main --tags
```

GitHub Actions bouwt de installer automatisch en maakt een Release aan.

---

## Opmerkingen

- Zorg dat Tesseract op het doelsysteem geïnstalleerd is in
  `C:\Program Files\Tesseract-OCR\tesseract.exe` (het standaardpad).
  Pas `core/ocr.py` aan als het pad afwijkt.
- De `--onedir`-modus is **vereist** voor PyMuPDF vanwege de native `.dll`-bestanden.
  De `--onefile`-modus wordt *niet* ondersteund.
- `--collect-all tkinterdnd2` is vereist voor de GUI; de DragDrop-executable
  gebruikt standaard Tkinter en heeft dit niet nodig.
