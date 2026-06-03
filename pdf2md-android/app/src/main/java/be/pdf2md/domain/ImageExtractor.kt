package be.pdf2md.domain

import android.content.Context
import android.util.Log
import be.pdf2md.BuildConfig
import com.artifex.mupdf.fitz.Document
import com.artifex.mupdf.fitz.Page
import java.io.File

private const val TAG = "ImageExtractor"

/**
 * Port van [extract_images_from_page] in pdf_utils.py.
 *
 * BUGFIX t.o.v. origineel: afbeeldingen worden ALTIJD geëxtraheerd,
 * ongeacht de hoeveelheid tekst op de pagina.
 */
object ImageExtractor {

    private val supportedExtensions = setOf("jpeg", "jpg", "png", "webp")

    /**
     * Extraheert alle ingebedde afbeeldingen van [page].
     *
     * Opslaglocatie hangt af van [backupEnabled]:
     * - `false` (default) → `context.cacheDir/images/` — nooit in Google Backup
     * - `true`            → `context.filesDir/images/` — wél in Google Backup
     *
     * Bestandsnaamformaat: `{pdfStem}_img_{pageNum}_{idx}.{ext}`
     * Exceptions per afbeelding worden gelogd en overgeslagen.
     *
     * @return lijst van [File] objecten voor elke opgeslagen afbeelding
     */
    fun extractFromPage(
        page: Page,
        doc: Document,
        context: Context,
        pdfStem: String,
        pageNum: Int,
        backupEnabled: Boolean = false,
    ): List<File> {
        val baseDir = if (backupEnabled) context.filesDir else context.cacheDir
        val outputDir = File(baseDir, "images").also { it.mkdirs() }
        val savedImages = mutableListOf<File>()

        val imageCount = page.countImages()
        for (idx in 0 until imageCount) {
            try {
                val imageInfo = page.getImage(idx)
                val imageBytes = doc.extractImage(imageInfo.number)
                    ?: continue

                val rawExt = imageInfo.type?.lowercase() ?: "png"
                val ext = if (rawExt in supportedExtensions) rawExt else "png"
                val filename = "${pdfStem}_img_${pageNum}_${idx}.${ext}"
                val outputFile = File(outputDir, filename)
                outputFile.writeBytes(imageBytes)
                savedImages.add(outputFile)
            } catch (e: Exception) {
                if (BuildConfig.DEBUG) Log.w(TAG, "Afbeelding $idx op pagina $pageNum overgeslagen: ${e.message}")
            }
        }

        return savedImages
    }
}
