# PDF2MD — MCP-server

Een [Model Context Protocol](https://modelcontextprotocol.io)-server die de
PDF2MD-functionaliteit als tools beschikbaar stelt aan een LLM-client (Claude
Desktop, Claude Code, …). Zo kan een LLM een PDF rechtstreeks als Markdown
inlezen — veel zuiniger met tokens dan de ruwe PDF — of een hele map PDF's in
één keer omzetten.

De server is een dunne laag bovenop het bestaande [`pdf2md/core`](../pdf2md)
-pakket; alle extractie-, OCR-, opmaak- en logica wordt hergebruikt.

## Tools

| Tool | Beschrijving | Resultaat |
|------|--------------|-----------|
| `pdf_to_markdown(pdf_path)` | Converteert één PDF naar Markdown-tekst (met OCR-fallback). Slaat geen afbeeldingen op. | Markdown-string |
| `extract_pdf_images(pdf_path, output_dir)` | Extraheert alle ingebedde afbeeldingen naar een map. | `{output_dir, image_count, images}` |
| `convert_pdf_directory(source_dir, output_dir=None)` | Converteert recursief een hele map PDF's naar `.md`-bestanden + afbeeldingen + Excel-logboek. | `{source_dir, output_dir, converted, errors, log}` |
| `pdf_info(pdf_path)` | Snelle metadata zonder conversie (pagina's, ingebedde afbeeldingen, of OCR nodig is). | `{pages, embedded_images, ocr_recommended, chars}` |

## Installatie

```bash
cd pdf2md-mcp
python -m venv .venv
. .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### OCR (optioneel)

De OCR-fallback gebruikt Tesseract. Installeer het als je gescande PDF's wilt
verwerken en zorg dat het vindbaar is:

- **Windows:** standaardpad `C:\Program Files\Tesseract-OCR\tesseract.exe`
  (zie de [pdf2md README](../pdf2md/README.md)).
- **Linux/macOS:** installeer via je pakketbeheerder (`apt install tesseract-ocr`
  / `brew install tesseract`). De server gebruikt automatisch het binary uit
  `PATH`.
- Afwijkend pad? Zet de omgevingsvariabele `TESSERACT_CMD` naar het volledige
  pad van het `tesseract`-binary.

Zonder Tesseract werkt alles behalve OCR; pagina's zonder leesbare tekst leveren
dan lege tekst op (geen crash).

## Server koppelen

De server praat over **stdio**. Draai hem vanuit een checkout van deze
repository (het `pdf2md/core`-pakket wordt via een relatief pad geïmporteerd).

### Claude Code (CLI)

```bash
claude mcp add pdf2md -- python /absoluut/pad/naar/PDF2MD/pdf2md-mcp/server.py
```

Gebruik het Python-binary uit je virtuele omgeving als je er een hebt
aangemaakt, bijv. `/absoluut/pad/naar/PDF2MD/pdf2md-mcp/.venv/bin/python`.

### Claude Desktop

Voeg toe aan `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "pdf2md": {
      "command": "python",
      "args": ["/absoluut/pad/naar/PDF2MD/pdf2md-mcp/server.py"],
      "env": {
        "TESSERACT_CMD": "/usr/bin/tesseract"
      }
    }
  }
}
```

`env` is optioneel — laat het weg als Tesseract al in `PATH` staat of als je
geen OCR nodig hebt.

### Lokaal testen

```bash
python server.py        # start de stdio-server (Ctrl-C om te stoppen)
```

Of met de MCP Inspector:

```bash
npx @modelcontextprotocol/inspector python server.py
```

## Voorbeeldprompts

> "Lees `~/Documenten/contract.pdf` in en vat de belangrijkste clausules samen."
> → de client roept `pdf_to_markdown` aan en leest de Markdown.

> "Zet alle PDF's in `~/Rapporten` om naar Markdown."
> → de client roept `convert_pdf_directory` aan; resultaat in `~/Rapporten_MD`.

## Licentie

GNU Affero General Public License v3.0 (AGPL v3) — gelijk aan het hoofdproject,
omdat PyMuPDF zelf AGPL v3 is. Zie [LICENSE](../LICENSE).
