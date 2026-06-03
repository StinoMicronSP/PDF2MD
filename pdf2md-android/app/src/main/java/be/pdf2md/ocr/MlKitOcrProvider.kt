package be.pdf2md.ocr

import android.content.Context
import android.graphics.Bitmap
import com.artifex.mupdf.fitz.ColorSpace
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
        val matrix = Matrix(scale, scale)
        // alpha=false → RGB (3 bytes per pixel), geen transparantie nodig voor OCR
        val pixmap = page.toPixmap(matrix, ColorSpace.DeviceRGB, false)

        // Gebruik pixmap.width/height als bron van waarheid — NIET de berekende
        // bounds-waarden. Afrondingsverschillen zorgen anders voor een
        // ArrayIndexOutOfBoundsException in getSamples().
        val pw = pixmap.width
        val ph = pixmap.height

        // getSamples() geeft ruwe RGB bytes terug (3 bytes per pixel).
        // Android Bitmap verwacht ARGB ints — handmatige conversie vereist.
        val samples = pixmap.getSamples()
        val intArray = IntArray(pw * ph) { i ->
            val r = samples[i * 3].toInt() and 0xFF
            val g = samples[i * 3 + 1].toInt() and 0xFF
            val b = samples[i * 3 + 2].toInt() and 0xFF
            (0xFF shl 24) or (r shl 16) or (g shl 8) or b
        }
        pixmap.destroy()

        val bitmap = Bitmap.createBitmap(pw, ph, Bitmap.Config.ARGB_8888)
        bitmap.setPixels(intArray, 0, pw, 0, 0, pw, ph)
        return bitmap
    }
}
