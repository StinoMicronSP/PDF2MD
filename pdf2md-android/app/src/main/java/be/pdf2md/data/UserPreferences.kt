package be.pdf2md.data

import android.content.Context
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

/**
 * Lichte wrapper rond SharedPreferences voor gebruikersinstellingen.
 * Exposeert een [StateFlow] zodat Compose-schermen reactief kunnen reageren
 * op wijzigingen zonder een zwaardere dependency zoals DataStore.
 */
class UserPreferences(context: Context) {

    private val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    private val _backupImages = MutableStateFlow(
        prefs.getBoolean(KEY_BACKUP_IMAGES, false),
    )

    /** Geeft aan of geëxtraheerde afbeeldingen opgeslagen worden in filesDir (wél in backup). */
    val backupImages: StateFlow<Boolean> = _backupImages.asStateFlow()

    fun setBackupImages(enabled: Boolean) {
        prefs.edit().putBoolean(KEY_BACKUP_IMAGES, enabled).apply()
        _backupImages.value = enabled
    }

    companion object {
        private const val PREFS_NAME = "pdf2md_prefs"
        private const val KEY_BACKUP_IMAGES = "backup_images"
    }
}
