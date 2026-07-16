package com.ddakpul.math

import android.app.Application
import android.content.Context
import com.ddakpul.math.core.common.LocaleManagerCompat
import com.ddakpul.math.presentation.common.SpeechSettings
import dagger.hilt.android.HiltAndroidApp

@HiltAndroidApp
class DdakPulApplication : Application() {
    // 앱 컨텍스트에도 저장된 언어를 입힌다 — @ApplicationContext로 문제은행을 읽는
    // AssetProblemSource가 올바른 언어의 리소스를 보게 하려면 여기가 진입점이다.
    override fun attachBaseContext(base: Context) {
        super.attachBaseContext(LocaleManagerCompat.wrap(base))
    }

    override fun onCreate() {
        super.onCreate()
        // 저장된 음성(TTS) 설정을 관찰 가능한 StateFlow로 끌어올린다 — 첫 화면부터 올바른 엔진.
        SpeechSettings.load(this)
    }
}
