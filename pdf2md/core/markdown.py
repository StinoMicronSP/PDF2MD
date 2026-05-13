"""Heuristic Markdown formatter for Dutch business PDF text."""


def format_line(line: str) -> str:
    """Apply heuristic Markdown formatting to a single text line.

    Rules (in order of priority):
    - All-uppercase line (3–80 chars, no dot, no leading digit) → H1 heading
    - Line ending with ":" and shorter than 60 chars → H2 subheading
    - Line starting with "-", "•", or "*" → unordered list item
    - Everything else → plain paragraph text

    Args:
        line: A raw text line from the PDF.

    Returns:
        The formatted Markdown line, or an empty string for blank lines.
    """
    stripped = line.strip()
    if not stripped:
        return ""

    if (
        stripped.isupper()
        and 3 <= len(stripped) <= 80
        and "." not in stripped
        and not any(c.isdigit() for c in stripped[:2])
    ):
        return f"# {stripped.title()}"

    if stripped.endswith(":") and len(stripped) < 60:
        return f"## {stripped}"

    if stripped[0] in ("-", "•", "*"):
        return f"- {stripped.lstrip('-•* ').strip()}"

    return stripped


def build_markdown(pages: list[str]) -> str:
    """Convert a list of per-page text strings into a single Markdown document.

    Pages are separated by a horizontal rule and an italic page-number label.
    Lines within each page are processed through :func:`format_line`.

    Args:
        pages: List of raw text strings, one per PDF page (1-indexed labelling).

    Returns:
        A complete Markdown string.
    """
    sections: list[str] = []
    for i, page_text in enumerate(pages, start=1):
        formatted_lines: list[str] = []
        for line in page_text.splitlines():
            result = format_line(line)
            formatted_lines.append(result)

        # Collapse consecutive blank lines into a single blank line
        collapsed: list[str] = []
        prev_blank = False
        for fl in formatted_lines:
            if fl == "":
                if not prev_blank:
                    collapsed.append("")
                prev_blank = True
            else:
                collapsed.append(fl)
                prev_blank = False

        page_body = "\n".join(collapsed).strip()
        sections.append(f"---\n*Pagina {i}*\n\n{page_body}")

    return "\n\n".join(sections)
