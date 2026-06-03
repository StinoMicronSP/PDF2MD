package be.pdf2md.ui

import android.content.Context
import android.net.Uri
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import be.pdf2md.data.UserPreferences
import be.pdf2md.domain.PdfProcessor
import be.pdf2md.domain.PdfResult
import be.pdf2md.export.MarkdownExporter
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

/** Alle mogelijke schermstatussen voor de conversie. */
sealed class ConversionState {
    object Idle : ConversionState()
    data class Processing(val currentPage: Int, val totalPages: Int) : ConversionState()
    data class Done(val result: PdfResult) : ConversionState()
    data class Error(val message: String) : ConversionState()
}

/** ExportState — resultaat van een exportpoging. */
sealed class ExportState {
    object Idle : ExportState()
    data class Success(val path: String) : ExportState()
    data class Error(val message: String) : ExportState()
}

class MainViewModel : ViewModel() {

    private val _conversionState = MutableStateFlow<ConversionState>(ConversionState.Idle)
    val conversionState: StateFlow<ConversionState> = _conversionState.asStateFlow()

    private val _exportState = MutableStateFlow<ExportState>(ExportState.Idle)
    val exportState: StateFlow<ExportState> = _exportState.asStateFlow()

    // Lazy initialisatie — context wordt pas bij eerste aanroep meegegeven
    private var _prefs: UserPreferences? = null

    fun prefs(context: Context): UserPreferences {
        if (_prefs == null) _prefs = UserPreferences(context.applicationContext)
        return _prefs!!
    }

    /** Start de PDF conversie vanuit [uri]. Leest backup-instelling uit [UserPreferences]. */
    fun convertPdf(uri: Uri, context: Context) {
        viewModelScope.launch {
            _conversionState.value = ConversionState.Processing(0, 0)
            val backupImages = prefs(context).backupImages.value
            runCatching {
                PdfProcessor(context).process(uri, backupImages) { current, total ->
                    _conversionState.value = ConversionState.Processing(current, total)
                }
            }.fold(
                onSuccess = { result -> _conversionState.value = ConversionState.Done(result) },
                onFailure = { e -> _conversionState.value = ConversionState.Error(e.message ?: "Onbekende fout") },
            )
        }
    }

    /** Exporteert het Markdown resultaat naar Downloads/ en wist daarna de tijdelijke cache. */
    fun exportMarkdown(context: Context, markdownText: String, filename: String) {
        viewModelScope.launch {
            runCatching {
                MarkdownExporter.export(context, markdownText, filename)
            }.fold(
                onSuccess = { path ->
                    // Alleen cacheDir wissen — filesDir/images blijft staan voor backup
                    clearTempCache(context)
                    _exportState.value = ExportState.Success(path)
                },
                onFailure = { e -> _exportState.value = ExportState.Error(e.message ?: "Export mislukt") },
            )
        }
    }

    /** Zet de state terug naar [ConversionState.Idle] en wist de tijdelijke cache. */
    fun reset(context: Context? = null) {
        context?.let { clearTempCache(it) }
        _conversionState.value = ConversionState.Idle
        _exportState.value = ExportState.Idle
    }

    /** Verwijdert tijdelijke afbeeldingen uit cacheDir. filesDir/images blijft intact voor backup. */
    private fun clearTempCache(context: Context) {
        context.cacheDir.resolve("images").deleteRecursively()
    }
}
