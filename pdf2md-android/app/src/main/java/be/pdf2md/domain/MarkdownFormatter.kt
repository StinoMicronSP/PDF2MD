package be.pdf2md.domain

import java.io.File

/**
 * Bouwt de uiteindelijke Markdown string op uit de resultaten van alle pagina's.
 *
 * Paginaformaat equivalent aan Python:
 * `all_text_parts.append(f"---\n*Pagina {page_num}*\n\n{text}")`
 * Gevolgd door `"\n\n".join(all_text_parts)`.
 */
object MarkdownFormatter {

    /**
     * Formatteert één pagina als Markdown sectie.
     *
     * @param pageNum  1-gebaseerd paginanummer
     * @param text     geëxtraheerde tekst van de pagina
     * @param images   opgeslagen afbeeldingsbestanden van deze pagina
     */
    fun formatPage(pageNum: Int, text: String, images: List<File>): String {
        val sb = StringBuilder()
        sb.append("---\n*Pagina $pageNum*\n\n")
        sb.append(text)

        if (images.isNotEmpty()) {
            sb.append("\n\n")
            images.forEach { file ->
                sb.append("![afbeelding](${file.name})\n")
            }
        }

        return sb.toString()
    }

    /**
     * Voegt alle geformatteerde paginasecties samen met `\n\n` als scheiding,
     * identiek aan Python's `"\n\n".join(all_text_parts)`.
     */
    fun combine(pages: List<String>): String = pages.joinToString("\n\n")
}
