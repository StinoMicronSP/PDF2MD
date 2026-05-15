package be.pdf2md.ui

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.lifecycle.viewmodel.compose.viewModel
import be.pdf2md.ui.screens.HomeScreen
import be.pdf2md.ui.screens.ResultScreen

class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        setContent {
            val viewModel: MainViewModel = viewModel()
            val state by viewModel.conversionState.collectAsState()

            Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
                when (val s = state) {
                    is ConversionState.Done -> {
                        ResultScreen(
                            viewModel = viewModel,
                            result = s.result,
                            onNavigateBack = { viewModel.reset() },
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
