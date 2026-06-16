#!/usr/bin/env python3
"""PDF2MD MCP-server.

Stelt de PDF2MD-functionaliteit (PDF -> Markdown, afbeeldingsextractie en
batch-mapconversie) beschikbaar als Model Context Protocol (MCP) tools, zodat
een LLM-client een PDF rechtstreeks als Markdown kan inlezen en tokens bespaart.

De server hergebruikt het bestaande ``pdf2md/core``-pakket; de map daarvan wordt
bij het importeren aan ``sys.path`` toegevoegd. Draai de server daarom vanuit een
checkout van deze repository.
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
from pathlib import Path

# --- Maak het bestaande pdf2md/core-pakket importeerbaar ---------------------
_REPO_ROOT = Path(__file__).resolve().parent.parent
_PDF2MD_PKG = _REPO_ROOT / "pdf2md"
if str(_PDF2MD_PKG) not in sys.path:
    sys.path.insert(0, str(_PDF2MD_PKG))

import core.ocr as _ocr  # noqa: E402
from core.markdown import format_line  # noqa: E402
from core.ocr import ocr_page  # noqa: E402
from core.pdf_utils import process_pdf  # noqa: E402
from core.processor import _PAGE_LABEL, process_directory  # noqa: E402

from mcp.server.fastmcp import FastMCP  # noqa: E402

# --- Platformonafhankelijk Tesseract-pad -------------------------------------
# core/ocr.py hardcodeert een Windows-pad; honoreer $TESSERACT_CMD of het
# systeembinary zodat OCR ook werkt waar de MCP-server ook draait. ocr_page
# leest deze modulevariabele bij elke aanroep opnieuw uit.
_tess = os.environ.get("TESSERACT_CMD") or shutil.which("tesseract")
if _tess:
    _ocr._TESSERACT_CMD = _tess

mcp = FastMCP("pdf2md")


def _convert_to_markdown(
    pdf_path: Path, image_dir: Path | None
) -> tuple[str, list[str]]:
    """Voer extractie + heuristische Markdown-opmaak uit op één PDF.

    Hergebruikt ``core.pdf_utils.process_pdf`` (tekst- en afbeeldingsextractie
    met OCR-fallback) en ``core.markdown.format_line`` (kop-/lijstheuristiek),
    en spiegelt wat ``core.processor.convert_pdf`` doet voordat het naar schijf
    schrijft.

    Args:
        pdf_path: Pad naar de bron-PDF.
        image_dir: Map om ingebedde afbeeldingen naar weg te schrijven. Bij
            ``None`` wordt een tijdelijke map gebruikt en worden de afbeeldingen
            weggegooid.

    Returns:
        ``(markdown_tekst, afbeeldingsbestandsnamen)``. De lijst is leeg wanneer
        ``image_dir`` ``None`` is.
    """
    discard = image_dir is None
    target_dir = Path(tempfile.mkdtemp(prefix="pdf2md_")) if discard else image_dir
    target_dir.mkdir(parents=True, exist_ok=True)
    try:
        full_text, images = process_pdf(pdf_path, target_dir, ocr_func=ocr_page)
    finally:
        if discard:
            shutil.rmtree(target_dir, ignore_errors=True)
            images = []

    formatted: list[str] = []
    for line in full_text.splitlines():
        stripped = line.strip()
        if stripped == "---" or _PAGE_LABEL.match(stripped):
            formatted.append(stripped)
        else:
            formatted.append(format_line(line))
    return "\n".join(formatted), images


@mcp.tool()
def pdf_to_markdown(pdf_path: str) -> str:
    """Converteer één PDF-bestand naar Markdown-tekst en geef die terug.

    Tekst wordt geëxtraheerd met PyMuPDF; pagina's met nauwelijks leesbare tekst
    vallen terug op Tesseract-OCR (Nederlands + Engels). Koppen, subkoppen en
    opsommingslijsten worden heuristisch herkend. Ingebedde afbeeldingen worden
    door deze tool NIET opgeslagen — gebruik daarvoor ``extract_pdf_images``.

    Gebruik dit om de inhoud van een PDF efficiënt in te lezen in plaats van de
    ruwe binary te laden.

    Args:
        pdf_path: Absoluut of relatief pad naar een ``.pdf``-bestand.

    Returns:
        De documentinhoud als Markdown-string.
    """
    path = Path(pdf_path).expanduser()
    if not path.is_file():
        raise FileNotFoundError(f"PDF niet gevonden: {path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Geen PDF-bestand: {path}")
    markdown, _ = _convert_to_markdown(path, image_dir=None)
    return markdown


@mcp.tool()
def extract_pdf_images(pdf_path: str, output_dir: str) -> dict:
    """Extraheer alle ingebedde afbeeldingen uit een PDF naar een map.

    Args:
        pdf_path: Pad naar het ``.pdf``-bestand.
        output_dir: Map om de afbeeldingen naar weg te schrijven (wordt
            aangemaakt indien nodig).

    Returns:
        Een dict met ``output_dir``, ``image_count`` en de lijst ``images``
        (bestandsnamen relatief aan ``output_dir``).
    """
    path = Path(pdf_path).expanduser()
    if not path.is_file():
        raise FileNotFoundError(f"PDF niet gevonden: {path}")
    out = Path(output_dir).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    _, images = process_pdf(path, out, ocr_func=ocr_page)
    return {
        "output_dir": str(out),
        "image_count": len(images),
        "images": images,
    }


@mcp.tool()
def convert_pdf_directory(source_dir: str, output_dir: str | None = None) -> dict:
    """Converteer recursief elke PDF in een mapstructuur naar Markdown op schijf.

    Spiegelt de mapstructuur onder de uitvoermap, schrijft per PDF één
    ``.md``-bestand, slaat ingebedde afbeeldingen ernaast op en schrijft een
    Excel-logboek (``conversie_log.xlsx``) plus ``app.log``. Dit is de
    batch-workflow om een hele map PDF's te "ontploffen".

    Args:
        source_dir: Map die recursief op ``*.pdf`` wordt doorzocht.
        output_dir: Doelmap. Standaard ``<source_dir>_MD``.

    Returns:
        Een dict met ``source_dir``, ``output_dir``, ``converted`` (aantal
        gelukt), ``errors`` en ``log`` (pad naar het Excel-logboek).
    """
    src = Path(source_dir).expanduser()
    if not src.is_dir():
        raise NotADirectoryError(f"Bronmap niet gevonden: {src}")
    out = (
        Path(output_dir).expanduser()
        if output_dir
        else src.parent / f"{src.name}_MD"
    )
    success, errors = process_directory(src, out)
    return {
        "source_dir": str(src),
        "output_dir": str(out),
        "converted": success,
        "errors": errors,
        "log": str(out / "conversie_log.xlsx"),
    }


@mcp.tool()
def pdf_info(pdf_path: str) -> dict:
    """Geef snelle metadata over een PDF terug zonder hem te converteren.

    Args:
        pdf_path: Pad naar het ``.pdf``-bestand.

    Returns:
        Een dict met ``pages``, ``embedded_images``, ``ocr_recommended`` (True
        wanneer minstens één pagina nauwelijks leesbare tekst bevat) en
        ``chars`` (totaal aantal leesbare tekens).
    """
    import fitz  # noqa: PLC0415

    path = Path(pdf_path).expanduser()
    if not path.is_file():
        raise FileNotFoundError(f"PDF niet gevonden: {path}")

    doc = fitz.open(str(path))
    try:
        pages = doc.page_count
        total_chars = 0
        images = 0
        ocr_recommended = False
        for page in doc:
            raw = page.get_text("text").strip()
            total_chars += len(raw)
            if len(raw) < 100:
                ocr_recommended = True
            images += len(page.get_images(full=True))
    finally:
        doc.close()
    return {
        "path": str(path),
        "pages": pages,
        "embedded_images": images,
        "ocr_recommended": ocr_recommended,
        "chars": total_chars,
    }


def main() -> None:
    """Draai de MCP-server over stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
