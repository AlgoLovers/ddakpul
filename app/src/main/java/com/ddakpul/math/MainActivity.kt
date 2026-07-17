package com.ddakpul.math

import android.content.Context
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.windowsizeclass.ExperimentalMaterial3WindowSizeClassApi
import androidx.compose.material3.windowsizeclass.calculateWindowSizeClass
import androidx.compose.ui.Modifier
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
                // 루트 배경을 테마로 항상 칠한다 — 안 칠하면 다크 모드에서 밝은 창 배경 위에
                // 다크 팔레트의 밝은 글씨가 올라가 안 보이는 사고가 난다(태블릿 레일 분기에서 실제 발생).
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background,
                ) {
                    val windowSizeClass = calculateWindowSizeClass(this)
                    AppRoot(windowSizeClass = windowSizeClass)
                }
            }
        }
    }
}
