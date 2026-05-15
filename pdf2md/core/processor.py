"""Orchestration: scan source directory → convert PDFs → write MD → log results."""

import logging
import re
from pathlib import Path
from typing import Callable, Optional

from .fuzzy import check_existing
from .logger import ConversionLogger, LogEntry
from .markdown import format_line
from .ocr import ocr_page
from .pdf_utils import process_pdf

logger = logging.getLogger(__name__)

_PAGE_LABEL = re.compile(r"^\*Pagina \d+\*$")


def sanitize(name: str) -> str:
    """Replace non-word characters (except hyphens) with underscores.

    Applied only to the file stem, not the extension.

    Args:
        name: The raw filename stem to sanitise.

    Returns:
        A filesystem-safe string.
    """
    return re.sub(r"[^\w\-]", "_", name)


def convert_pdf(
    pdf_path: Path,
    source_root: Path,
    output_root: Path,
) -> tuple[str, list[str], Optional[str], float]:
    """Convert a single PDF to Markdown and write it to the mirror output path.

    Args:
        pdf_path: Absolute path to the source PDF.
        source_root: Root of the source directory (used to compute relative paths).
        output_root: Root of the output directory tree.

    Returns:
        A tuple of (status, image_files, fuzzy_match, similarity_score).
        *status* is one of ``"OK"``, ``"OCR_GEBRUIKT"``, ``"DUPLICATE_RISK"``.

    Raises:
        Exception: Re-raised after logging so the caller can decide how to handle it.
    """
    relative = pdf_path.relative_to(source_root)
    clean_stem = sanitize(pdf_path.stem)
    output_md_path = output_root / relative.parent / f"{clean_stem}.md"
    output_dir = output_md_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # Extract text/images
    full_text, image_files = process_pdf(pdf_path, output_dir, ocr_func=ocr_page)

    # Apply line-by-line Markdown heuristics, but skip separator lines that
    # process_pdf already inserted ("---" and "*Pagina N*") so they are not
    # misidentified as bullet points by format_line.
    formatted_lines = []
    for line in full_text.splitlines():
        stripped = line.strip()
        if stripped == "---" or _PAGE_LABEL.match(stripped):
            formatted_lines.append(stripped)
        else:
            formatted_lines.append(format_line(line))
    markdown_content = "\n".join(formatted_lines)

    ocr_used = _detect_ocr_used(pdf_path)

    # Fuzzy duplicate check before writing
    fuzzy_match, similarity_score = check_existing(output_md_path, output_root)

    if fuzzy_match and similarity_score > 90:
        status = "DUPLICATE_RISK"
        logger.warning(
            "DUPLICATE_RISK: '%s' closely matches existing '%s' (score=%.1f)",
            output_md_path.name,
            fuzzy_match,
            similarity_score,
        )
    elif ocr_used:
        status = "OCR_GEBRUIKT"
    else:
        status = "OK"

    output_md_path.write_text(markdown_content, encoding="utf-8")
    logger.info("Written: %s [%s]", output_md_path, status)

    return status, image_files, fuzzy_match, similarity_score


def _detect_ocr_used(pdf_path: Path) -> bool:
    """Heuristic: consider OCR used when any page has fewer than 100 raw chars.

    Args:
        pdf_path: Path to the PDF.

    Returns:
        True if OCR was likely used for at least one page.
    """
    try:
        import fitz  # noqa: PLC0415

        doc = fitz.open(str(pdf_path))
        ocr_triggered = False
        try:
            for _, page in enumerate(doc):
                raw = page.get_text("text")
                if len(raw.strip()) < 100:
                    ocr_triggered = True
                    break
        finally:
            doc.close()
        return ocr_triggered
    except Exception:  # noqa: BLE001
        return False


def process_directory(
    source_dir: Path,
    output_dir: Path,
    progress_callback: Optional[Callable[[int, int, str], None]] = None,
) -> tuple[int, int]:
    """Recursively convert all PDFs in *source_dir* and write results to *output_dir*.

    Args:
        source_dir: Root directory to scan for ``*.pdf`` files.
        output_dir: Root directory for mirrored output.
        progress_callback: Optional callable invoked as
            ``callback(current, total, filename)`` after each file attempt.

    Returns:
        A tuple of (success_count, error_count).
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    log_path = output_dir / "conversie_log.xlsx"
    app_log_path = output_dir / "app.log"

    _configure_file_logging(app_log_path)

    conv_logger = ConversionLogger()

    pdf_files = sorted(source_dir.rglob("*.pdf"))
    total = len(pdf_files)
    success = 0
    errors = 0

    logger.info("Starting conversion of %d PDF(s) from '%s'", total, source_dir)

    for idx, pdf_path in enumerate(pdf_files, start=1):
        try:
            status, image_files, fuzzy_match, similarity_score = convert_pdf(
                pdf_path, source_dir, output_dir
            )
            relative_stem = sanitize(pdf_path.stem)
            relative_parent = pdf_path.relative_to(source_dir).parent
            output_md = str(output_dir / relative_parent / f"{relative_stem}.md")

            conv_logger.add(
                LogEntry(
                    originele_pdf=str(pdf_path),
                    output_md=output_md,
                    afbeeldingen=len(image_files),
                    fuzzy_match=fuzzy_match,
                    similarity_score=similarity_score,
                    status=status,
                )
            )
            success += 1
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to convert '%s': %s", pdf_path, exc)
            conv_logger.add(
                LogEntry(
                    originele_pdf=str(pdf_path),
                    output_md="",
                    afbeeldingen=0,
                    fuzzy_match=None,
                    similarity_score=0.0,
                    status="FOUT",
                )
            )
            errors += 1

        if progress_callback:
            progress_callback(idx, total, pdf_path.name)

    conv_logger.save(log_path)
    logger.info(
        "Conversion complete: %d OK, %d errors. Log: %s", success, errors, log_path
    )
    return success, errors


def _configure_file_logging(log_path: Path) -> None:
    """Add a file handler to the root logger for *log_path*.

    Safe to call multiple times; duplicate handlers are avoided.

    Args:
        log_path: Path to the log file to write.
    """
    root = logging.getLogger()
    for handler in root.handlers:
        if isinstance(handler, logging.FileHandler) and handler.baseFilename == str(
            log_path
        ):
            return  # already configured
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)-8s %(name)s: %(message)s")
    )
    root.addHandler(fh)
