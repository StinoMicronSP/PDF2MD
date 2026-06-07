# PDF2MD

Converteer PDF-bestanden (rapporten, contracten, zakelijke documenten) naar
Markdown. Ondersteunt tekstuele PDF's met een lichte OCR-fallback via Tesseract
voor gescande pagina's.

## Functies

- **Recursieve verwerking** — verwerkt alle `.pdf`-bestanden in een bronmap en
  bewaart de mapstructuur in de uitvoermap.
- **Heuristische Markdown-opmaak** — herkent koppen (volledig hoofdletters),
  subkoppen (eindigen op `:`) en opsommingslijsten.
- **OCR-fallback** — pagina's met minder dan 100 tekens worden automatisch via
  Tesseract verwerkt.
- **Afbeeldingsextractie** — embedded afbeeldingen worden opgeslagen als `.png`
  naast het `.md`-bestand, met inline Markdown-verwijzingen.
- **Fuzzy-duplicaatdetectie** — detecteert of een vergelijkbare `.md`-naam al
  bestaat (drempel: 90 % gelijkenis).
- **Excel-logboek** — `conversie_log.xlsx` in de uitvoermap met statussen
  `OK`, `OCR_GEBRUIKT`, `FOUT` en `DUPLICATE_RISK`.
- **GUI** (Tkinter) en **drag-and-drop CLI**.

## Vereisten

### Python-paketten

```
pip install -r requirements.txt
```

### Tesseract-OCR (vereist voor OCR-fallback)

Download de Windows-installer:
<https://github.com/UB-Mannheim/tesseract/wiki>

Selecteer tijdens de installatie de extra talen **Nederlands (`nld`)** en
**Engels (`eng`)**.

Standaard installatiepad: `C:\Program Files\Tesseract-OCR\tesseract.exe`

> Als u Tesseract op een afwijkend pad installeert, pas dan de regel
> `pytesseract.pytesseract.tesseract_cmd` in `core/ocr.py` aan.

## Gebruik

### GUI

```bat
python apps/main_gui.py
```

1. Klik op **Bladeren…** naast *Bronmap* en selecteer de map met PDF's.
2. De *Doelmap* wordt automatisch ingesteld op `<bronmap>_MD`.
   U kunt dit aanpassen.
3. Klik op **Starten**. De voortgangsbalk toont de voortgang per bestand.
4. Na afloop verschijnt een samenvatting.

### Drag & Drop (CLI)

Sleep een map op `PDF2MD_DragDrop.exe` of voer uit:

```bat
python apps/dragdrop.py "C:\pad\naar\map"
```

De uitvoer wordt geschreven naar `C:\pad\naar\map_MD\`.

## Uitvoerstructuur

```
bronmap_MD/
├── submap/
│   ├── document.md
│   ├── document_img_1_0.png   ← geëxtraheerde afbeelding (indien aanwezig)
│   └── …
├── conversie_log.xlsx
└── app.log
```

## Excel-logboek — kolomindeling

| Kolom              | Beschrijving                                      |
|--------------------|---------------------------------------------------|
| `originele_pdf`    | Volledig pad naar het bronbestand                 |
| `output_md`        | Volledig pad naar het gegenereerde `.md`-bestand  |
| `afbeeldingen`     | Aantal geëxtraheerde afbeeldingsbestanden         |
| `fuzzy_match`      | Naam van het meest gelijkende bestaande `.md`     |
| `similarity_score` | Gelijkenis in procent (0–100)                     |
| `status`           | `OK` / `OCR_GEBRUIKT` / `FOUT` / `DUPLICATE_RISK` |

## Buildbare installer

Zie [build_instructions.md](build_instructions.md) voor instructies om
`.exe`-bestanden en een Inno Setup-installer te genereren.

## Licentie

GNU Affero General Public License v3.0 (AGPL v3)

Dit project is open source. Je mag de broncode vrij gebruiken, aanpassen en
distribueren, maar **elke distributie (ook als installer) vereist dat je de
volledige broncode beschikbaar stelt** onder dezelfde AGPL v3-licentie.

Zie het [LICENSE](../LICENSE)-bestand voor de volledige tekst.

> **Waarom AGPL v3?** Dit project gebruikt PyMuPDF, dat zelf AGPL v3 is.
> De licentie van een dependency bepaalt de minimale licentie van het project.
