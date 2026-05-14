"""Tesseract OCR fallback for image-heavy or scan-based PDF pages."""

import logging

logger = logging.getLogger(__name__)

_TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def ocr_page(page) -> str:  # type: ignore[type-arg]  # fitz.Page has no stub
    """Run Tesseract OCR on a single PyMuPDF page and return extracted text.

    The page is rasterised at 2× zoom for better recognition quality.
    pytesseract and Pillow are imported lazily so a missing Tesseract
    installation only causes a warning, not a startup crash.
    Returns an empty string on any error so callers can continue processing.

    Args:
        page: A ``fitz.Page`` object.

    Returns:
        The OCR-extracted text, or an empty string on failure.
    """
    try:
        import fitz  # noqa: PLC0415
        import pytesseract  # noqa: PLC0415
        from PIL import Image  # noqa: PLC0415

        pytesseract.pytesseract.tesseract_cmd = _TESSERACT_CMD

        matrix = fitz.Matrix(2, 2)
        pix = page.get_pixmap(matrix=matrix)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        text: str = pytesseract.image_to_string(img, lang="nld+eng")
        return text
    except Exception as exc:  # noqa: BLE001
        logger.warning("OCR failed on page %s: %s", getattr(page, "number", "?"), exc)
        return ""
