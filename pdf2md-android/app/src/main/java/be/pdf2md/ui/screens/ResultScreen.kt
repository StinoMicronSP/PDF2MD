package be.pdf2md.ui.screens

import android.Manifest
import android.content.pm.PackageManager
import android.os.Build
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.selection.SelectionContainer
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Snackbar
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.ContextCompat
import be.pdf2md.R
import be.pdf2md.domain.PdfResult
import be.pdf2md.ui.ExportState
import be.pdf2md.ui.MainViewModel

/**
 * Resultaatscherm: scrollbare Markdown preview + export- en terugknop.
 *
 * Op Android 8/9 (API 26–28) wordt WRITE_EXTERNAL_STORAGE gevraagd vóór
 * de export. Op API 29+ regelt MediaStore het zonder extra permissie.
 */
@Composable
fun ResultScreen(
    viewModel: MainViewModel,
    result: PdfResult,
    onNavigateBack: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    val exportState by viewModel.exportState.collectAsState()

    // Permissie-launcher: wordt alleen gebruikt op API 26–28
    val writePermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission(),
    ) { granted ->
        if (granted) {
            viewModel.exportMarkdown(context, result.markdownText, "pdf2md_export")
        }
    }

    fun startExport() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.Q &&
            ContextCompat.checkSelfPermission(
                context, Manifest.permission.WRITE_EXTERNAL_STORAGE,
            ) != PackageManager.PERMISSION_GRANTED
        ) {
            writePermissionLauncher.launch(Manifest.permission.WRITE_EXTERNAL_STORAGE)
        } else {
            viewModel.exportMarkdown(context, result.markdownText, "pdf2md_export")
        }
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(16.dp),
    ) {
        Text(
            text = stringResource(R.string.result_title),
            style = MaterialTheme.typography.titleLarge,
        )

        Spacer(modifier = Modifier.height(8.dp))

        // Scrollbare Markdown preview — tekst is selecteerbaar
        SelectionContainer(
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth()
                .verticalScroll(rememberScrollState()),
        ) {
            Text(
                text = result.markdownText,
                fontFamily = FontFamily.Monospace,
                fontSize = 13.sp,
                lineHeight = 20.sp,
            )
        }

        Spacer(modifier = Modifier.height(12.dp))

        // Export status feedback
        when (val s = exportState) {
            is ExportState.Success -> {
                Snackbar(modifier = Modifier.padding(bottom = 8.dp)) {
                    Text(stringResource(R.string.export_success, s.path))
                }
            }
            is ExportState.Error -> {
                Snackbar(
                    modifier = Modifier.padding(bottom = 8.dp),
                    containerColor = MaterialTheme.colorScheme.errorContainer,
                ) {
                    Text(stringResource(R.string.export_error, s.message))
                }
            }
            is ExportState.Idle -> Unit
        }

        Button(
            onClick = { startExport() },
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(stringResource(R.string.btn_export))
        }

        Spacer(modifier = Modifier.height(8.dp))

        OutlinedButton(
            onClick = {
                viewModel.reset(context)
                onNavigateBack()
            },
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(stringResource(R.string.btn_again))
        }
    }
}
