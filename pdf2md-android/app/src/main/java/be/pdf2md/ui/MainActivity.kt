package be.pdf2md.ui

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.lifecycle.viewmodel.compose.viewModel
import be.pdf2md.R
import be.pdf2md.ui.screens.HomeScreen
import be.pdf2md.ui.screens.ResultScreen
import be.pdf2md.ui.screens.SettingsScreen

@OptIn(ExperimentalMaterial3Api::class)
class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        setContent {
            val viewModel: MainViewModel = viewModel()
            val state by viewModel.conversionState.collectAsState()
            val context = LocalContext.current
            var showSettings by rememberSaveable { mutableStateOf(false) }

            if (showSettings) {
                SettingsScreen(
                    viewModel = viewModel,
                    onNavigateBack = { showSettings = false },
                )
                return@setContent
            }

            Scaffold(
                modifier = Modifier.fillMaxSize(),
                topBar = {
                    if (state !is ConversionState.Done) {
                        TopAppBar(
                            title = { Text(stringResource(R.string.app_name)) },
                            actions = {
                                IconButton(onClick = { showSettings = true }) {
                                    Icon(
                                        imageVector = Icons.Default.Settings,
                                        contentDescription = stringResource(R.string.settings_title),
                                    )
                                }
                            },
                        )
                    }
                },
            ) { innerPadding ->
                when (val s = state) {
                    is ConversionState.Done -> {
                        ResultScreen(
                            viewModel = viewModel,
                            result = s.result,
                            onNavigateBack = { viewModel.reset(context) },
                            modifier = Modifier.padding(innerPadding),
                        )
                    }
                    else -> {
                        HomeScreen(
                            viewModel = viewModel,
                            onNavigateToResult = {},
                            modifier = Modifier.padding(innerPadding),
                        )
                    }
                }
            }
        }
    }
}
