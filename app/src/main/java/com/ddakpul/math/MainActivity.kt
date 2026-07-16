package com.ddakpul.math

import android.content.Context
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.material3.windowsizeclass.ExperimentalMaterial3WindowSizeClassApi
import androidx.compose.material3.windowsizeclass.calculateWindowSizeClass
import com.ddakpul.math.core.common.LocaleManagerCompat
import com.ddakpul.math.core.designsystem.theme.DdakPulTheme
import com.ddakpul.math.ui.AppRoot
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    // 앱 안에서 고른 언어(한국어/English)를 액티비티 리소스에 입힌다 — 시스템 언어와 무관하게.
    override fun attachBaseContext(newBase: Context) {
        super.attachBaseContext(LocaleManagerCompat.wrap(newBase))
    }

    @OptIn(ExperimentalMaterial3WindowSizeClassApi::class)
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            DdakPulTheme {
                val windowSizeClass = calculateWindowSizeClass(this)
                AppRoot(windowSizeClass = windowSizeClass)
            }
        }
    }
}
