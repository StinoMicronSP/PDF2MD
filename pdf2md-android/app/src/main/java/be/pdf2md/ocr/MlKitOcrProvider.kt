package be.pdf2md.ocr

import android.content.Context
import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Color
import com.artifex.mupdf.fitz.Matrix
import com.artifex.mupdf.fitz.Page
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.text.TextRecognition
import com.google.mlkit.vision.text.latin.TextRecognizerOptions
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException

/**
 * Vervangt de `ocr_func` parameter uit [process_pdf] in pdf_utils.py.
 *
 * Rendert de MuPDF pagina als bitmap en herkent tekst via ML Kit
 * (volledig offline, geen internet vereist).
 */
object MlKitOcrProvider {

    private val recognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)

    /**
     * Herkent tekst op [page] via ML Kit OCR.
     * Geeft null terug bij een lege resultaatset.
     */
    suspend fun recognize(page: Page, @Suppress("UNUSED_PARAMETER") context: Context): String? {
        val bitmap = renderPageToBitmap(page)
        val inputImage = InputImage.fromBitmap(bitmap, 0)

        return suspendCancellableCoroutine { cont ->
            recognizer.process(inputImage)
                .addOnSuccessListener { result ->
                    val text = result.text.trim()
                    cont.resume(text.ifEmpty { null })
                }
                .addOnFailureListener { e ->
                    cont.resumeWithException(e)
                }
        }
    }

    private fun renderPageToBitmap(page: Page, scale: Float = 2f): Bitmap {
        val bounds = page.bounds
        val width = (bounds.x1 * scale).toInt()
        val height = (bounds.y1 * scale).toInt()

        val bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
        val canvas = Canvas(bitmap)
        canvas.drawColor(Color.WHITE)

        val matrix = Matrix(scale, scale)
        val pixmap = page.toPixmap(matrix, com.artifex.mupdf.fitz.ColorSpace.DeviceRGB, false)
        val pixels = IntArray(width * height)
        pixmap.toIntArray(pixels, 0, width, 0, 0, width, height)
        bitmap.setPixels(pixels, 0, width, 0, 0, width, height)
        pixmap.destroy()

        return bitmap
    }
}
