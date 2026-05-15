package be.pdf2md.domain

import com.artifex.mupdf.fitz.Page

/**
 * Port van [extract_page_text] in pdf_utils.py.
 *
 * Extraheert platte tekst uit één MuPDF pagina en verwijdert
 * omringende witruimte (equivalent aan Python's .strip()).
 */
object TextExtractor {

    /**
     * Geeft de ruwe tekst van [page] terug, witruimte getrimd.
     * Retourneert een lege string als de pagina geen tekst bevat.
     */
    fun extract(page: Page): String =
        try {
            page.toStructuredText("preserve-whitespace").toString().trim()
        } catch (e: Exception) {
            ""
        }
}
