package be.pdf2md.domain

import android.content.Context
import android.util.Log
import be.pdf2md.BuildConfig
import com.artifex.mupdf.fitz.Document
import com.artifex.mupdf.fitz.PDFDocument
import com.artifex.mupdf.fitz.Page
import java.io.File

private const val TAG = "ImageExtractor"

/**
 * Port van [extract_images_from_page] in pdf_utils.py.
 *
 * BUGFIX t.o.v. origineel: afbeeldingen worden ALTIJD geëxtraheerd,
 * ongeacht de hoeveelheid tekst op de pagina.
 *
 * Implementatie: navigeert via PDFDocument → Page XObject resources →
 * Image subtype → PDFDocument.newPixmapFromImage() → PNG bytes.
 * Equivalent aan Python's doc.extract_image(xref).
 */
object ImageExtractor {

    /**
     * Extraheert alle ingebedde afbeeldingen van [page].
     *
     * Opslaglocatie hangt af van [backupEnabled]:
     * - `false` (default) → `context.cacheDir/images/`  — nooit in Google Backup
     * - `true`            → `context.filesDir/images/`  — wél in Google Backup
     *
     * Bestandsnaamformaat: `{pdfStem}_img_{pageNum}_{idx}.png`
     * Exceptions per afbeelding worden gelogd en overgeslagen.
     *
     * @return lijst van [File] objecten voor elke opgeslagen afbeelding
     */
    fun extractFromPage(
        @Suppress("UNUSED_PARAMETER") page: Page,
        doc: Document,
        context: Context,
        pdfStem: String,
        pageNum: Int,
        backupEnabled: Boolean = false,
    ): List<File> {
        val pdfDoc = doc as? PDFDocument ?: return emptyList()
        val baseDir = if (backupEnabled) context.filesDir else context.cacheDir
        val outputDir = File(baseDir, "images").also { it.mkdirs() }
        val savedImages = mutableListOf<File>()

        try {
            // findPage() verwacht een 0-gebaseerde index; retourneert null bij ongeldige pagina
            val pageObj = pdfDoc.findPage(pageNum - 1) ?: return savedImages
            val resources = pageObj.get("Resources")?.resolve() ?: return savedImages
            val xObjects = resources.get("XObject")?.resolve() ?: return savedImages
            val keys: Array<String> = xObjects.keys() ?: return savedImages

            keys.forEachIndexed { idx, key ->
                try {
                    val xobj = xObjects.get(key)?.resolve() ?: return@forEachIndexed
                    val subtype = xobj.get("Subtype")?.asName() ?: return@forEachIndexed
                    if (subtype != "Image") return@forEachIndexed

                    val pixmap = pdfDoc.newPixmapFromImage(xobj) ?: return@forEachIndexed
                    val pngBytes = pixmap.asPNG()
                    pixmap.destroy()

                    val filename = "${pdfStem}_img_${pageNum}_${idx}.png"
                    val outputFile = File(outputDir, filename)
                    outputFile.writeBytes(pngBytes)
                    savedImages.add(outputFile)
                } catch (e: Exception) {
                    if (BuildConfig.DEBUG) {
                        Log.w(TAG, "Afbeelding '$key' op pagina $pageNum overgeslagen: ${e.message}")
                    }
                }
            }
        } catch (e: Exception) {
            if (BuildConfig.DEBUG) {
                Log.w(TAG, "Image-extractie overgeslagen voor pagina $pageNum: ${e.message}")
            }
        }

        return savedImages
    }
}
