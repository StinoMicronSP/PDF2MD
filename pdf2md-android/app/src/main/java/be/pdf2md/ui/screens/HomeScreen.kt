package be.pdf2md.ui.screens

import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import be.pdf2md.R
import be.pdf2md.ui.ConversionState
import be.pdf2md.ui.MainViewModel

/**
 * Startscherm: PDF selecteren en voortgang weergeven.
 * Navigeert automatisch naar [onNavigateToResult] zodra de conversie klaar is.
 */
@Composable
fun HomeScreen(
    viewModel: MainViewModel,
    onNavigateToResult: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    val state by viewModel.conversionState.collectAsState()

    val pdfPicker = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetContent(),
    ) { uri ->
        uri?.let { viewModel.convertPdf(it, context) }
    }

    LaunchedEffect(state) {
        if (state is ConversionState.Done) {
            onNavigateToResult()
        }
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(24.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        when (val s = state) {
            is ConversionState.Idle -> {
                Button(
                    onClick = { pdfPicker.launch("application/pdf") },
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Text(stringResource(R.string.btn_pick_pdf))
                }
            }

            is ConversionState.Processing -> {
                CircularProgressIndicator()
                Spacer(modifier = Modifier.height(16.dp))
                val progressText = if (s.totalPages > 0) {
                    stringResource(R.string.processing_progress, s.currentPage, s.totalPages)
                } else {
                    stringResource(R.string.processing_loading)
                }
                Text(
                    text = progressText,
                    style = MaterialTheme.typography.bodyMedium,
                )
            }

            is ConversionState.Error -> {
                Text(
                    text = stringResource(R.string.error_prefix, s.message),
                    color = MaterialTheme.colorScheme.error,
                    style = MaterialTheme.typography.bodyMedium,
                )
                Spacer(modifier = Modifier.height(16.dp))
                Button(
                    onClick = { viewModel.reset() },
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Text(stringResource(R.string.btn_try_again))
                }
            }

            is ConversionState.Done -> Unit
        }
    }
}
