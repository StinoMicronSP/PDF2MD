"""
pdf_utils.py — PDF tekst- en afbeeldingsextractie via PyMuPDF (fitz)

BUGFIX t.o.v. originele versie:
  De drempelconditie (if len(text) < 200) blokkeerde afbeeldingsextractie
  op alle pagina's met voldoende tekst — zoals onderhoudschecklist-PDF's.
  Afbeeldingen worden nu ALTIJD geëxtraheerd, ongeacht tekstlengte.
"""

import fitz  # PyMuPDF
import re
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def extract_page_text(page: fitz.Page) -> str:
    """Extraheer tekstinhoud van een enkele PDF-pagina."""
    return page.get_text("text").strip()


def extract_images_from_page(
    page: fitz.Page,
    doc: fitz.Document,
    output_dir: Path,
    pdf_stem: str,
    page_num: int,
) -> list[str]:
    """
    Extraheer alle embedded afbeeldingen van een pagina.

    Args:
        page:       fitz.Page object
        doc:        het volledige fitz.Document (nodig voor xref lookup)
        output_dir: map waar afbeeldingen naast het .md-bestand komen
        pdf_stem:   bestandsnaam van de PDF zonder extensie
        page_num:   paginanummer (1-gebaseerd) voor bestandsnaming

    Returns:
        Lijst van relatieve bestandsnamen (voor Markdown-referenties)
    """
    saved_images = []
    images = page.get_images(full=True)

    if not images:
        return saved_images

    for idx, img_info in enumerate(images):
        xref = img_info[0]

        try:
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]  # bijv. "jpeg", "png"

            # Sla op als PNG wanneer ext onbekend of problematisch is
            if image_ext not in ("jpeg", "jpg", "png", "webp"):
                image_ext = "png"

            filename = f"{pdf_stem}_img_{page_num}_{idx}.{image_ext}"
            output_path = output_dir / filename

            output_path.write_bytes(image_bytes)
            saved_images.append(filename)
            logger.debug(f"Afbeelding opgeslagen: {output_path}")

        except Exception as e:
            logger.warning(f"Afbeelding {xref} op pagina {page_num} overgeslagen: {e}")
            continue

    return saved_images


def process_pdf(
    pdf_path: Path,
    output_dir: Path,
    ocr_func=None,
) -> tuple[str, list[str]]:
    """
    Verwerk een PDF-bestand: extraheer tekst + afbeeldingen van alle pagina's.

    Args:
        pdf_path:   pad naar het PDF-bestand
        output_dir: map voor afbeeldingsoutput
        ocr_func:   optionele OCR-functie (wordt aangeroepen als tekst < 100 tekens/pagina)

    Returns:
        Tuple van (volledige tekst als string, lijst van afbeeldingsbestandsnamen)
    """
    doc = fitz.open(str(pdf_path))
    pdf_stem = re.sub(r"[^\w\-]", "_", pdf_path.stem)
    all_text_parts = []
    all_images = []

    for page_num, page in enumerate(doc, start=1):
        text = extract_page_text(page)

        # OCR-fallback: alleen bij echt weinig tekst (gescande pagina's)
        if len(text) < 100 and ocr_func is not None:
            logger.info(f"Pagina {page_num}: OCR-fallback (tekst={len(text)} tekens)")
            text = ocr_func(page) or text

        # Paginascheiding in Markdown
        all_text_parts.append(f"---\n*Pagina {page_num}*\n\n{text}")

        # ✅ BUGFIX: altijd afbeeldingen extraheren, geen drempelconditie
        # Reden: checklist-PDF's bevatten zowel tekst ALS ingebedde foto's
        page_images = extract_images_from_page(
            page, doc, output_dir, pdf_stem, page_num
        )
        all_images.extend(page_images)

    doc.close()
    full_text = "\n\n".join(all_text_parts)
    return full_text, all_images
