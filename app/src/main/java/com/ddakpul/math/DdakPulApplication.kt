package com.ddakpul.math

import android.app.Application
import com.ddakpul.math.presentation.common.SpeechSettings
import dagger.hilt.android.HiltAndroidApp

@HiltAndroidApp
class DdakPulApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        // 저장된 음성(TTS) 설정을 관찰 가능한 StateFlow로 끌어올린다 — 첫 화면부터 올바른 엔진.
        SpeechSettings.load(this)
    }
}
