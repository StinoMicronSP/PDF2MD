package be.pdf2md.ui.screens

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
import be.pdf2md.R
import be.pdf2md.domain.PdfResult
import be.pdf2md.ui.ExportState
import be.pdf2md.ui.MainViewModel

/**
 * Resultaatscherm: scrollbare Markdown preview + export- en terugknop.
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
            onClick = {
                viewModel.exportMarkdown(
                    context = context,
                    markdownText = result.markdownText,
                    filename = "pdf2md_export",
                )
            },
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
