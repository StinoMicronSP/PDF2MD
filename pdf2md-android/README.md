# pdf2md-android

Android port van [`pdf_utils.py`](../pdf2md/core/pdf_utils.py) — een offline PDF naar Markdown converter.

## Oorsprong

Dit project is een 1-op-1 Kotlin port van de Python module `pdf_utils.py` die gebruik maakt
van PyMuPDF (fitz) voor tekst- en afbeeldingsextractie uit PDF bestanden.

| Python (origineel) | Kotlin (deze app) |
|---|---|
| `process_pdf()` | `PdfProcessor.kt` |
| `extract_page_text()` | `TextExtractor.kt` |
| `extract_images_from_page()` | `ImageExtractor.kt` |
| `ocr_func` parameter | `MlKitOcrProvider.kt` |
| Bestandsuitvoer via `pathlib` | `MarkdownExporter.kt` via MediaStore |

## BUGFIX t.o.v. originele Python versie

De originele `pdf_utils.py` had een drempelconditie (`if len(text) < 200`) die
afbeeldingsextractie blokkeerde op alle pagina's met voldoende tekst.
Deze Android port lost dat op: **afbeeldingen worden altijd geëxtraheerd**,
ongeacht de hoeveelheid tekst op de pagina.

## Tech stack

| Laag | Keuze |
|---|---|
| Taal | Kotlin |
| PDF engine | MuPDF Android (`com.artifex.mupdf:viewer:1.23.0`) |
| OCR fallback | ML Kit Text Recognition v2 (offline) |
| UI | Jetpack Compose + Material 3 |
| Async | Kotlin Coroutines + Flow |
| Export | Android MediaStore API |

## Minimum vereisten

- Android 8.0 (API 26) of hoger
- Geen internetverbinding nodig (volledig offline)

## Gebruik

1. Tik op **"PDF kiezen"** en selecteer een PDF bestand
2. De app converteert pagina voor pagina (voortgangsindicator zichtbaar)
3. Bekijk de Markdown preview in het resultaatscherm
4. Tik op **"Exporteer naar Downloads"** om het `.md` bestand op te slaan
