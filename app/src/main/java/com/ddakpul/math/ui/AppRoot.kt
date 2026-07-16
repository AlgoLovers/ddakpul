package com.ddakpul.math.ui

import androidx.compose.material3.windowsizeclass.WindowSizeClass
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.ddakpul.math.presentation.onboarding.OnboardingScreen
import com.ddakpul.math.presentation.onboarding.OnboardingViewModel

/**
 * 앱 최상위 진입점 — 첫 실행이면 온보딩을, 이미 마쳤으면 본화면(탭)을 보여준다.
 * 완료 여부는 로컬 DB에서 관찰하므로 확인 전(null)에는 잠깐 빈 화면이다(아주 짧음).
 */
@Composable
fun AppRoot(
    windowSizeClass: WindowSizeClass,
    onboardingViewModel: OnboardingViewModel = hiltViewModel(),
) {
    val onboardingComplete by onboardingViewModel.onboardingComplete.collectAsStateWithLifecycle()
    when (onboardingComplete) {
        null -> Unit
        false -> OnboardingScreen(onComplete = onboardingViewModel::complete)
        true -> DdakPulApp(windowSizeClass = windowSizeClass)
    }
}
