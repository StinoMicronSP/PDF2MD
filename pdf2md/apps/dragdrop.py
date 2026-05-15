"""
dragdrop.py — Drag & Drop entry point voor PDF2MD

Gebruik:
    PDF2MD_DragDrop.exe "C:\\pad\\naar\\map"

Windows geeft het gesleepte pad mee als sys.argv[1].
Werkt ook als rechtsklik-handler via de Windows context menu registry entry.
"""

import logging
import sys
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

# Voeg projectroot toe aan sys.path zodat core-modules vindbaar zijn
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.processor import process_directory  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def get_source_path() -> Path | None:
    """Haal het bronpad op uit sys.argv.

    Windows geeft het pad mee als eerste argument bij drag-on-exe en
    rechtsklik. Paden met spaties kunnen omsloten zijn door aanhalingstekens.

    Returns:
        Een bestaand Path, of None als er geen geldig argument is.
    """
    if len(sys.argv) < 2:
        return None
    raw = " ".join(sys.argv[1:]).strip().strip('"').strip("'")
    path = Path(raw)
    return path if path.exists() else None


def validate_source(path: Path) -> str | None:
    """Valideer het bronpad.

    Args:
        path: Het te valideren pad.

    Returns:
        Een foutmelding als het pad ongeldig is, anders None.
    """
    if not path.exists():
        return f"Pad bestaat niet:\n{path}"
    if path.is_file():
        if path.suffix.lower() != ".pdf":
            return f"Gesleept bestand is geen PDF:\n{path.name}"
        return None
    if path.is_dir():
        if not list(path.rglob("*.pdf")):
            return f"Geen PDF-bestanden gevonden in:\n{path}"
        return None
    return f"Ongeldig pad:\n{path}"


def resolve_folders(source: Path) -> tuple[Path, Path]:
    """Bepaal de bronmap en outputmap.

    Als een enkel PDF-bestand gesleept werd, gebruik de bovenliggende map.

    Args:
        source: Het gesleepte pad (bestand of map).

    Returns:
        Tuple van (bronmap, outputmap).
    """
    source_dir = source.parent if source.is_file() else source
    output_dir = source_dir.parent / (source_dir.name + "_MD")
    return source_dir, output_dir


def main() -> None:
    """Verwerk het gesleepte pad en toon een resultaat-popup."""
    root = tk.Tk()
    root.withdraw()

    source = get_source_path()

    if source is None:
        messagebox.showerror(
            "PDF2MD — Geen invoer",
            "Gebruik: sleep een map of PDF op PDF2MD_DragDrop.exe\n\n"
            "Of gebruik via rechtsklik → 'Converteer naar Markdown'",
        )
        root.destroy()
        sys.exit(1)

    error_msg = validate_source(source)
    if error_msg:
        messagebox.showerror("PDF2MD — Ongeldig pad", error_msg)
        root.destroy()
        sys.exit(1)

    source_dir, output_dir = resolve_folders(source)
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Bron: %s", source_dir)
    logger.info("Output: %s", output_dir)

    root.destroy()

    # process_directory schrijft zelf conversie_log.xlsx en app.log
    success, errors = process_directory(source_dir, output_dir)

    root2 = tk.Tk()
    root2.withdraw()
    if errors == 0:
        messagebox.showinfo(
            "PDF2MD — Voltooid",
            f"{success} bestand(en) succesvol geconverteerd.\n\nOutput: {output_dir}",
        )
    else:
        messagebox.showwarning(
            "PDF2MD — Voltooid met fouten",
            f"{success} geconverteerd\n{errors} fout(en)\n\n"
            f"Controleer conversie_log.xlsx in:\n{output_dir}",
        )
    root2.destroy()


if __name__ == "__main__":
    main()
