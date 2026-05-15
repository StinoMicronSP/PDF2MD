"""Excel-based conversion log using pandas + openpyxl."""

import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd


@dataclass
class LogEntry:
    """Single row in the conversion log."""

    originele_pdf: str
    output_md: str
    afbeeldingen: int
    fuzzy_match: Optional[str]
    similarity_score: float
    status: str


class ConversionLogger:
    """Accumulates log entries and writes them atomically to an Excel file."""

    COLUMNS = [
        "originele_pdf",
        "output_md",
        "afbeeldingen",
        "fuzzy_match",
        "similarity_score",
        "status",
    ]

    def __init__(self) -> None:
        """Initialise an empty list of entries."""
        self._entries: list[LogEntry] = []

    def add(self, entry: LogEntry) -> None:
        """Append a log entry."""
        self._entries.append(entry)

    def save(self, log_path: Path) -> None:
        """Write all entries to *log_path* atomically via a temp file.

        Uses a NamedTemporaryFile so a partial write never corrupts an
        existing log file.
        """
        rows = [
            {
                "originele_pdf": e.originele_pdf,
                "output_md": e.output_md,
                "afbeeldingen": e.afbeeldingen,
                "fuzzy_match": e.fuzzy_match or "",
                "similarity_score": round(e.similarity_score, 2),
                "status": e.status,
            }
            for e in self._entries
        ]
        df = pd.DataFrame(rows, columns=self.COLUMNS)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            tmp_path = tmp.name

        df.to_excel(tmp_path, index=False)
        shutil.move(tmp_path, log_path)
