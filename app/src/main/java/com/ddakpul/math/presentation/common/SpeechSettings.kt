package com.ddakpul.math.presentation.common

import android.content.Context

/**
 * 읽어주기(TTS) 음성 설정 — 기기 로컬 UI 설정이라 학습 데이터(Room)와 분리해 가볍게 저장한다.
 * 어떤 TTS 엔진을 쓸지(enginePackage)와 말하기 속도(rate)만 담는다.
 * enginePackage가 null이면 기기 기본 엔진을 쓴다(삼성/구글 등 사용자 기본값).
 */
object SpeechSettings {
    private const val PREF = "ddakpul_speech"
    private const val KEY_ENGINE = "engine_package"
    private const val KEY_RATE = "speech_rate"

    /** 보통(1.0) 기준. 느리게 0.8 ~ 빠르게 1.2. 저학년은 살짝 느린 편이 알아듣기 쉽다. */
    const val DEFAULT_RATE = 1.0f

    private fun prefs(context: Context) = context.getSharedPreferences(PREF, Context.MODE_PRIVATE)

    fun enginePackage(context: Context): String? = prefs(context).getString(KEY_ENGINE, null)

    fun setEnginePackage(
        context: Context,
        pkg: String?,
    ) {
        prefs(context)
            .edit()
            .apply {
                if (pkg == null) remove(KEY_ENGINE) else putString(KEY_ENGINE, pkg)
            }.apply()
    }

    fun rate(context: Context): Float = prefs(context).getFloat(KEY_RATE, DEFAULT_RATE)

    fun setRate(
        context: Context,
        rate: Float,
    ) {
        prefs(context).edit().putFloat(KEY_RATE, rate).apply()
    }
}
