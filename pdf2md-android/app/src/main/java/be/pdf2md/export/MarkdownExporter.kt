package be.pdf2md.export

import android.content.ContentValues
import android.content.Context
import android.os.Build
import android.os.Environment
import android.provider.MediaStore
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.File
import java.io.FileOutputStream

/**
 * Schrijft de geconverteerde Markdown tekst naar `Downloads/` via de
 * Android MediaStore API — equivalent aan Python's `output_path.write_bytes(...)`.
 */
object MarkdownExporter {

    /**
     * Exporteert [markdownText] naar `Downloads/{filename}.md`.
     * Op Android 10+ wordt MediaStore gebruikt; op oudere versies rechtstreeks
     * naar `Environment.DIRECTORY_DOWNLOADS`.
     *
     * @return het pad of de URI als string van het opgeslagen bestand
     */
    suspend fun export(
        context: Context,
        markdownText: String,
        filename: String,
    ): String = withContext(Dispatchers.IO) {
        val safeFilename = filename.removeSuffix(".md") + ".md"

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            exportViaMediaStore(context, markdownText, safeFilename)
        } else {
            exportLegacy(markdownText, safeFilename)
        }
    }

    private fun exportViaMediaStore(
        context: Context,
        content: String,
        filename: String,
    ): String {
        val values = ContentValues().apply {
            put(MediaStore.Downloads.DISPLAY_NAME, filename)
            put(MediaStore.Downloads.MIME_TYPE, "text/markdown")
            put(MediaStore.Downloads.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS)
        }

        val uri = context.contentResolver.insert(
            MediaStore.Downloads.EXTERNAL_CONTENT_URI,
            values,
        ) ?: error("MediaStore kon het bestand niet aanmaken")

        context.contentResolver.openOutputStream(uri)?.use { stream ->
            stream.write(content.toByteArray(Charsets.UTF_8))
        } ?: error("Kan niet schrijven naar $uri")

        return uri.toString()
    }

    @Suppress("DEPRECATION")
    private fun exportLegacy(content: String, filename: String): String {
        val downloadsDir = Environment.getExternalStoragePublicDirectory(
            Environment.DIRECTORY_DOWNLOADS,
        )
        downloadsDir.mkdirs()
        val file = File(downloadsDir, filename)
        FileOutputStream(file).use { it.write(content.toByteArray(Charsets.UTF_8)) }
        return file.absolutePath
    }
}
