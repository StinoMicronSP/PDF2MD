"""PDF text and image extraction using PyMuPDF (fitz)."""

import logging
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF

from .ocr import ocr_page

logger = logging.getLogger(__name__)

# Thresholds
_OCR_THRESHOLD = 100   # chars per page below which OCR is triggered
_IMG_THRESHOLD = 200   # chars per page below which images are extracted


def extract_pages(
    pdf_path: Path,
    output_dir: Path,
    stem: str,
) -> tuple[list[str], list[str]]:
    """Extract text and images from all pages of a PDF.

    For each page:
    - If extracted text is shorter than ``_OCR_THRESHOLD`` chars, the page is
      processed through the Tesseract OCR fallback.
    - If the page has fewer than ``_IMG_THRESHOLD`` chars of text, embedded
      images are saved next to the output .md file and Markdown image references
      are appended to the page text.

    Args:
        pdf_path: Path to the source PDF file.
        output_dir: Directory where image files will be saved.
        stem: Sanitised base name (without extension) used for image filenames.

    Returns:
        A tuple of:
        - ``pages``: list of per-page text strings (possibly augmented with
          Markdown image references).
        - ``image_files``: list of saved image file paths (as strings).
    """
    pages: list[str] = []
    image_files: list[str] = []
    ocr_used = False

    doc = fitz.open(str(pdf_path))
    try:
        for page_num, page in enumerate(doc):
            text: str = page.get_text("text")

            if len(text.strip()) < _OCR_THRESHOLD:
                logger.debug(
                    "Page %d of '%s' has <100 chars — using OCR", page_num + 1, pdf_path.name
                )
                ocr_text = ocr_page(page)
                if ocr_text.strip():
                    text = ocr_text
                    ocr_used = True

            # Image extraction for low-text pages
            if len(text.strip()) < _IMG_THRESHOLD:
                img_refs = _extract_images(doc, page, page_num, output_dir, stem)
                image_files.extend(img_refs)
                if img_refs:
                    md_refs = "\n".join(
                        f"![afbeelding]({Path(p).name})" for p in img_refs
                    )
                    text = f"{text}\n{md_refs}"

            pages.append(text)
    finally:
        doc.close()

    return pages, image_files


def _extract_images(
    doc: fitz.Document,
    page: fitz.Page,
    page_num: int,
    output_dir: Path,
    stem: str,
) -> list[str]:
    """Extract and save all embedded images from a single page.

    Args:
        doc: The open fitz.Document.
        page: The page to extract images from.
        page_num: Zero-based page index (used for filename labelling).
        output_dir: Directory to write PNG files into.
        stem: Sanitised file stem used as part of the image filename.

    Returns:
        List of saved image file paths as strings.
    """
    saved: list[str] = []
    for img_index, img_info in enumerate(page.get_images(full=True)):
        xref = img_info[0]
        try:
            base_img = doc.extract_image(xref)
            img_bytes = base_img["image"]
            img_ext = base_img.get("ext", "png")
            img_filename = f"{stem}_img_{page_num + 1}_{img_index}.{img_ext}"
            img_path = output_dir / img_filename
            img_path.write_bytes(img_bytes)
            saved.append(str(img_path))
            logger.debug("Saved image: %s", img_path)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Could not extract image xref=%d from page %d: %s", xref, page_num + 1, exc
            )
    return saved
