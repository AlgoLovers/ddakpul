package com.ddakpul.math

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.material3.windowsizeclass.ExperimentalMaterial3WindowSizeClassApi
import androidx.compose.material3.windowsizeclass.calculateWindowSizeClass
import com.ddakpul.math.core.designsystem.theme.DdakPulTheme
import com.ddakpul.math.ui.DdakPulApp
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    @OptIn(ExperimentalMaterial3WindowSizeClassApi::class)
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            DdakPulTheme {
                val windowSizeClass = calculateWindowSizeClass(this)
                DdakPulApp(windowSizeClass = windowSizeClass)
            }
        }
    }
}
