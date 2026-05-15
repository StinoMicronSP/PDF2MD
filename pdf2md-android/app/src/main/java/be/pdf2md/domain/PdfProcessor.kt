package be.pdf2md.domain

import android.content.Context
import android.net.Uri
import android.util.Log
import be.pdf2md.ocr.MlKitOcrProvider
import com.artifex.mupdf.fitz.Document
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.File

private const val TAG = "PdfProcessor"
private const val OCR_THRESHOLD = 100

/**
 * Port van [process_pdf] in pdf_utils.py.
 *
 * Verwerkt een PDF pagina voor pagina: tekst extraheren, optionele OCR fallback,
 * afbeeldingen extraheren (ALTIJD, ongeacht tekstlengte — zie BUGFIX) en
 * het resultaat samenstellen als Markdown.
 */
class PdfProcessor(private val context: Context) {

    /**
     * Converteert de PDF aangeduid door [uri] naar een [PdfResult].
     * Roept [onProgress] aan na elke verwerkte pagina met (huidigePagina, totaalPagina's).
     *
     * Equivalent aan Python's `process_pdf(pdf_path, output_dir, ocr_func)`.
     */
    suspend fun process(
        uri: Uri,
        onProgress: (current: Int, total: Int) -> Unit = { _, _ -> },
    ): PdfResult = withContext(Dispatchers.IO) {
        val inputStream = context.contentResolver.openInputStream(uri)
            ?: error("Kan het PDF bestand niet openen")

        val pdfBytes = inputStream.use { it.readBytes() }
        val doc = Document.openDocument(pdfBytes, "")
        val pdfStem = resolveFileName(uri).removeSuffix(".pdf")

        val pageCount = doc.countPages()
        val pageSections = mutableListOf<String>()
        val allImages = mutableListOf<File>()

        for (pageIndex in 0 until pageCount) {
            val pageNum = pageIndex + 1
            val page = doc.loadPage(pageIndex)

            try {
                var text = TextExtractor.extract(page)

                // OCR fallback als tekst te kort is — zelfde drempel (100) als Python
                if (text.length < OCR_THRESHOLD) {
                    val ocrText = runCatching {
                        MlKitOcrProvider.recognize(page, context)
                    }.getOrNull()
                    if (!ocrText.isNullOrBlank()) text = ocrText
                }

                // Afbeeldingen ALTIJD extraheren (BUGFIX: geen tekstdrempel hier)
                val pageImages = ImageExtractor.extractFromPage(
                    page = page,
                    doc = doc,
                    context = context,
                    pdfStem = pdfStem,
                    pageNum = pageNum,
                )
                allImages.addAll(pageImages)

                pageSections.add(MarkdownFormatter.formatPage(pageNum, text, pageImages))
            } catch (e: Exception) {
                Log.e(TAG, "Fout op pagina $pageNum: ${e.message}")
                pageSections.add(MarkdownFormatter.formatPage(pageNum, "", emptyList()))
            } finally {
                page.destroy()
            }

            onProgress(pageNum, pageCount)
        }

        doc.destroy()

        PdfResult(
            markdownText = MarkdownFormatter.combine(pageSections),
            imageFiles = allImages,
        )
    }

    private fun resolveFileName(uri: Uri): String {
        return try {
            context.contentResolver.query(uri, null, null, null, null)?.use { cursor ->
                val nameIndex = cursor.getColumnIndex(android.provider.OpenableColumns.DISPLAY_NAME)
                cursor.moveToFirst()
                cursor.getString(nameIndex)
            } ?: "document.pdf"
        } catch (e: Exception) {
            "document.pdf"
        }
    }
}

/** Resultaat van één PDF conversie. */
data class PdfResult(
    val markdownText: String,
    val imageFiles: List<File>,
)
