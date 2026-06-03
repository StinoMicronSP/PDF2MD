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
     * Extraheert alle ingebedde afbeeldingen van [page] en slaat ze op in
     * `context.cacheDir/images/`. Bestandsnaamformaat:
     * `{pdfStem}_img_{pageNum}_{idx}.{ext}`
     *
     * Exceptions per afbeelding worden gelogd en overgeslagen (zelfde gedrag
     * als de Python try/except + continue).
     *
     * @return lijst van [File] objecten voor elke opgeslagen afbeelding
     */
    fun extractFromPage(
        page: Page,
        doc: Document,
        context: Context,
        pdfStem: String,
        pageNum: Int,
    ): List<File> {
        val outputDir = File(context.cacheDir, "images").also { it.mkdirs() }
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
