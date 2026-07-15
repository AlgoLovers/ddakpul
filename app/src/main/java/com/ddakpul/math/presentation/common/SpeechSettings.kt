package com.ddakpul.math.presentation.common

import android.content.Context
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

/**
 * 읽어주기(TTS) 음성 설정 — 기기 로컬 UI 설정이라 학습 데이터(Room)와 분리해 가볍게 저장한다.
 *
 * 핵심: 선택을 **관찰 가능한 StateFlow**로 노출한다. 예전엔 SharedPreferences를 한 번만 읽어
 * 화면 재구성 타이밍에 의존했는데, 그래서 "설정을 바꿔도 반영이 안 되고 늘 같은 엔진으로 읽는"
 * 버그가 있었다. 이제 [engine]·[rate]가 바뀌면 이를 구독하는 모든 화면(미리듣기·문제 읽기)이
 * 즉시 새 엔진으로 다시 붙는다.
 *
 * [enginePackage]가 null이면 기기 기본 엔진(삼성/구글 등 사용자 기본값)을 쓴다.
 * [engineLabel]은 사용자에게 "지금 어떤 음성으로 읽는지" 명확히 보여주기 위해 함께 저장한다.
 */
object SpeechSettings {
    private const val PREF = "ddakpul_speech"
    private const val KEY_ENGINE = "engine_package"
    private const val KEY_ENGINE_LABEL = "engine_label"
    private const val KEY_RATE = "speech_rate"

    /** 보통(1.0) 기준. 느리게 0.8 ~ 빠르게 1.2. 저학년은 살짝 느린 편이 알아듣기 쉽다. */
    const val DEFAULT_RATE = 1.0f

    private val _engine = MutableStateFlow<String?>(null)

    /** 선택된 TTS 엔진 패키지(null이면 기기 기본). 바뀌면 스피커가 즉시 재구성된다. */
    val engine: StateFlow<String?> = _engine.asStateFlow()

    private val _engineLabel = MutableStateFlow<String?>(null)

    /** 선택된 엔진의 표시 이름("갤럭시 음성" 등). 어떤 음성으로 읽는지 UI에 명확히 보여준다. */
    val engineLabel: StateFlow<String?> = _engineLabel.asStateFlow()

    private val _rate = MutableStateFlow(DEFAULT_RATE)

    /** 말하기 속도. */
    val rate: StateFlow<Float> = _rate.asStateFlow()

    @Volatile
    private var loaded = false

    private fun prefs(context: Context) = context.getSharedPreferences(PREF, Context.MODE_PRIVATE)

    /** 앱 시작 시 1회 호출 — 저장된 값을 StateFlow로 끌어올린다(이후엔 flow가 진실의 원천). */
    fun load(context: Context) {
        if (loaded) return
        val p = prefs(context)
        _engine.value = p.getString(KEY_ENGINE, null)
        _engineLabel.value = p.getString(KEY_ENGINE_LABEL, null)
        _rate.value = p.getFloat(KEY_RATE, DEFAULT_RATE)
        loaded = true
    }

    /** 엔진 선택. [pkg]가 null이면 기기 기본. [label]은 사용자에게 보여줄 이름. */
    fun setEngine(
        context: Context,
        pkg: String?,
        label: String?,
    ) {
        prefs(context)
            .edit()
            .apply {
                if (pkg == null) remove(KEY_ENGINE) else putString(KEY_ENGINE, pkg)
                if (label == null) remove(KEY_ENGINE_LABEL) else putString(KEY_ENGINE_LABEL, label)
            }.apply()
        _engine.value = pkg
        _engineLabel.value = label
    }

    fun setRate(
        context: Context,
        rate: Float,
    ) {
        prefs(context).edit().putFloat(KEY_RATE, rate).apply()
        _rate.value = rate
    }
}
