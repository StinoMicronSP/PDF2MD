"""CLI drag-and-drop handler: accepts a folder path via sys.argv[1]."""

import logging
import sys
from pathlib import Path
from tkinter import messagebox

from core.processor import process_directory

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Validate the dropped path and run the conversion, then show a result popup.

    Expects exactly one argument: the path to the source directory.
    """
    if len(sys.argv) < 2:
        messagebox.showerror(
            "PDF2MD",
            "Gebruik: sleep een map op dit programma om PDF's te converteren.",
        )
        sys.exit(1)

    source_path = Path(sys.argv[1])

    if not source_path.exists():
        messagebox.showerror("PDF2MD", f"Pad bestaat niet:\n{source_path}")
        sys.exit(1)

    if not source_path.is_dir():
        messagebox.showerror("PDF2MD", f"Dit is geen map:\n{source_path}")
        sys.exit(1)

    output_path = source_path.parent / f"{source_path.name}_MD"

    logger.info("Drag-drop conversion: '%s' → '%s'", source_path, output_path)

    try:
        success, errors = process_directory(source_path, output_path)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Conversion failed")
        messagebox.showerror("PDF2MD – Fout", f"Conversie mislukt:\n{exc}")
        sys.exit(1)

    messagebox.showinfo(
        "PDF2MD – Gereed",
        f"Conversie voltooid.\n\n"
        f"Verwerkt: {success} bestand(en)\n"
        f"Fouten:   {errors}\n\n"
        f"Uitvoer: {output_path}",
    )


if __name__ == "__main__":
    main()
