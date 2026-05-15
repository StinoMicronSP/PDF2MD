"""Tkinter GUI for the PDF2MD converter with drag-and-drop support."""

import logging
import re
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from tkinterdnd2 import DND_FILES, TkinterDnD

from core.processor import process_directory

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class PDF2MDApp(TkinterDnD.Tk):
    """Main application window for the PDF2MD converter."""

    def __init__(self) -> None:
        """Initialise the window, layout, and widget state."""
        super().__init__()
        self.title("PDF2MD Converter")
        self.geometry("520x380")
        self.resizable(False, False)

        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        """Create and arrange all widgets."""
        pad = {"padx": 10, "pady": 5}

        # Source directory row
        tk.Label(self, text="Bronmap:", anchor="w", width=12).grid(
            row=0, column=0, **pad, sticky="w"
        )
        self._src_var = tk.StringVar()
        tk.Entry(self, textvariable=self._src_var, width=42).grid(
            row=0, column=1, **pad
        )
        tk.Button(self, text="Bladeren…", command=self._browse_source).grid(
            row=0, column=2, **pad
        )

        # Destination directory row
        tk.Label(self, text="Doelmap:", anchor="w", width=12).grid(
            row=1, column=0, **pad, sticky="w"
        )
        self._dst_var = tk.StringVar()
        tk.Entry(self, textvariable=self._dst_var, width=42).grid(
            row=1, column=1, **pad
        )
        tk.Button(self, text="Bladeren…", command=self._browse_dest).grid(
            row=1, column=2, **pad
        )

        # Start button
        self._start_btn = tk.Button(
            self, text="Starten", command=self._start_conversion, width=16
        )
        self._start_btn.grid(row=2, column=1, pady=8)

        # Progress bar
        self._progress = ttk.Progressbar(
            self, orient="horizontal", length=460, mode="determinate"
        )
        self._progress.grid(row=3, column=0, columnspan=3, padx=10, pady=4)

        # Status label
        self._status_var = tk.StringVar(value="Klaar om te starten.")
        tk.Label(self, textvariable=self._status_var, anchor="w", fg="gray").grid(
            row=4, column=0, columnspan=3, padx=10, sticky="w"
        )

        # Drop zone
        self._build_dropzone(row=5)

    def _build_dropzone(self, row: int) -> None:
        """Create a drag-and-drop zone and register it as a DnD target.

        Accepts a folder or one or more PDF files. On drop, the source field
        is filled and the destination field is set automatically.

        Args:
            row: The grid row in which to place the drop zone frame.
        """
        frame = tk.LabelFrame(
            self,
            text="Of sleep hier een map of PDF-bestanden naartoe",
            padx=10,
            pady=8,
            relief="dashed",
            bd=2,
            fg="gray",
        )
        frame.grid(row=row, column=0, columnspan=3, padx=10, pady=(4, 10), sticky="ew")

        self._drop_label = tk.Label(
            frame,
            text="📂  Sleep een map of meerdere PDF's hier naartoe",
            fg="gray",
            pady=12,
        )
        self._drop_label.pack(fill="x")

        # Hover feedback
        def on_enter(event: tk.Event) -> None:
            frame.config(fg="blue", bd=3)

        def on_leave(event: tk.Event) -> None:
            frame.config(fg="gray", bd=2)

        # Drop handler
        def handle_drop(event: tk.Event) -> None:
            raw = event.data.strip()
            # Windows wraps paths that contain spaces in curly braces
            parts = re.findall(r"\{[^}]+\}|\S+", raw)
            paths = [Path(p.strip("{}")) for p in parts]
            resolved = [p for p in paths if p.exists()]

            if not resolved:
                messagebox.showwarning(
                    "Ongeldig pad", "Geen geldig bestand of map herkend."
                )
                return

            dirs = [p for p in resolved if p.is_dir()]
            if dirs:
                self._on_folder_dropped(dirs[0])
                return

            pdfs = [p for p in resolved if p.suffix.lower() == ".pdf"]
            if pdfs:
                self._on_folder_dropped(pdfs[0].parent)
                return

            messagebox.showwarning(
                "Niet ondersteund",
                "Sleep een map of één of meerdere PDF-bestanden.",
            )

        for widget in (frame, self._drop_label):
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind("<<Drop>>", handle_drop)
            widget.dnd_bind("<<DragEnter>>", on_enter)
            widget.dnd_bind("<<DragLeave>>", on_leave)

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_folder_dropped(self, folder: Path) -> None:
        """Fill source and destination fields when a folder is dropped.

        Args:
            folder: The resolved source directory path.
        """
        self._src_var.set(str(folder))
        self._dst_var.set(str(folder.parent / (folder.name + "_MD")))
        self._status_var.set(f"Map gesleept: {folder.name}  — klik Starten om te beginnen.")

    def _browse_source(self) -> None:
        """Open a directory chooser and populate the source field."""
        path = filedialog.askdirectory(title="Selecteer bronmap")
        if path:
            self._src_var.set(path)
            if not self._dst_var.get():
                self._dst_var.set(f"{path}_MD")

    def _browse_dest(self) -> None:
        """Open a directory chooser and populate the destination field."""
        path = filedialog.askdirectory(title="Selecteer doelmap")
        if path:
            self._dst_var.set(path)

    def _start_conversion(self) -> None:
        """Validate input paths and launch conversion in a background thread."""
        src = self._src_var.get().strip()
        dst = self._dst_var.get().strip()

        if not src:
            messagebox.showwarning("Invoer ontbreekt", "Selecteer eerst een bronmap.")
            return

        src_path = Path(src)
        if not src_path.is_dir():
            messagebox.showerror("Ongeldige bronmap", f"'{src}' is geen geldige map.")
            return

        dst_path = Path(dst) if dst else Path(f"{src}_MD")
        self._dst_var.set(str(dst_path))

        self._start_btn.config(state="disabled")
        self._progress["value"] = 0
        self._status_var.set("Bezig…")

        thread = threading.Thread(
            target=self._run_conversion,
            args=(src_path, dst_path),
            daemon=True,
        )
        thread.start()

    def _run_conversion(self, src_path: Path, dst_path: Path) -> None:
        """Execute the conversion and update the GUI from the worker thread."""
        pdf_count = len(list(src_path.rglob("*.pdf")))
        self._progress["maximum"] = max(pdf_count, 1)

        def on_progress(current: int, total: int, filename: str) -> None:
            self._progress["value"] = current
            self._status_var.set(f"Verwerken: {filename} ({current}/{total})")
            self.update_idletasks()

        try:
            success, errors = process_directory(src_path, dst_path, on_progress)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Unexpected error during conversion")
            self.after(0, lambda: self._on_done_error(str(exc)))
            return

        self.after(0, lambda: self._on_done(success, errors))

    def _on_done(self, success: int, errors: int) -> None:
        """Re-enable the UI and display the completion summary."""
        self._start_btn.config(state="normal")
        self._progress["value"] = self._progress["maximum"]
        self._status_var.set(
            f"Gereed: {success} bestand(en) verwerkt, {errors} fout(en)."
        )
        messagebox.showinfo(
            "Conversie voltooid",
            f"{success} bestand(en) verwerkt\n{errors} fout(en)",
        )

    def _on_done_error(self, message: str) -> None:
        """Re-enable the UI and show an error dialog."""
        self._start_btn.config(state="normal")
        self._status_var.set("Fout opgetreden.")
        messagebox.showerror("Fout", f"Onverwachte fout:\n{message}")


def main() -> None:
    """Entry point for the GUI application."""
    app = PDF2MDApp()
    app.mainloop()


if __name__ == "__main__":
    main()
