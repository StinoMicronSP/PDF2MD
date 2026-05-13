"""Fuzzy filename matching to detect potential duplicate output files."""

from pathlib import Path
from typing import Optional

from rapidfuzz import fuzz, process


def check_existing(
    output_md_path: Path, output_dir: Path
) -> tuple[Optional[str], float]:
    """Compare *output_md_path*'s filename against all .md files in *output_dir*.

    Returns the best matching filename and its similarity score when the score
    exceeds 90, otherwise returns (None, 0.0).

    Args:
        output_md_path: The path of the .md file that is about to be written.
        output_dir: The directory to search for existing .md files.

    Returns:
        A tuple of (matched_filename_or_None, score).
    """
    existing = [f.name for f in output_dir.rglob("*.md")]
    if not existing:
        return None, 0.0

    result = process.extractOne(
        output_md_path.name,
        existing,
        scorer=fuzz.token_sort_ratio,
    )
    if result and result[1] > 90:
        return result[0], float(result[1])
    return None, 0.0
