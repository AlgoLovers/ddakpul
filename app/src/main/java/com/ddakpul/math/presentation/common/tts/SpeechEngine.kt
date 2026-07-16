package com.ddakpul.math.presentation.common.tts

import android.content.Context
import android.os.Handler
import android.os.Looper
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import java.util.Locale

/**
 * 읽어주기 엔진 추상화 — 시스템 TTS(삼성/구글)와 (추후) 온디바이스 신경망 모델을
 * **같은 인터페이스**로 다룬다. 여러 백엔드를 얹어도 화면 코드는 이 계약만 알면 된다.
 *
 * 재생 상태([onSpeakingChanged])를 콜백으로 알려, 재생/정지 토글과 "지금 읽는 중" 표시를
 * 정확히 그릴 수 있게 한다.
 */
interface SpeechEngine {
    /** 사용자에게 보여줄 이름(예: "갤럭시 음성", "Supertonic"). */
    val label: String

    /** 텍스트를 읽는다. 이미 읽는 중이면 새 문장으로 갈아탄다(flush). */
    fun speak(text: String)

    /** 재생을 멈춘다. */
    fun stop()

    /** 엔진 자원 해제(화면을 벗어날 때). */
    fun release()
}

/**
 * 안드로이드 시스템 TTS 백엔드. 선택된 엔진 패키지(삼성/구글 등)로 붙고, 없으면 기기 기본.
 * 오프라인 원칙에 따라 네트워크 없이 되는 한국어 음성을 우선한다.
 *
 * [onSpeakingChanged]로 재생 시작/종료를 알린다 — 토글·표시가 실제 재생과 어긋나지 않게.
 */
class SystemSpeechEngine(
    context: Context,
    private val enginePackage: String?,
    private val rate: Float,
    override val label: String,
    // 읽을 언어 — 앱 언어(한국어 ⇄ English)를 따른다. 하드코딩하면 영어 모드에서 영어 문장을
    // 한국어 로케일로 읽거나(발음 붕괴) 한국어 데이터 없는 기기에서 조용히 실패한다.
    private val locale: Locale = Locale.KOREAN,
    private val onSpeakingChanged: (Boolean) -> Unit,
    // 실제로 붙은 엔진의 사람이 읽는 이름을 알려준다(기기 기본을 골랐을 때 "기기 기본" 대신
    // "Google 음성 인식 및 합성" 같은 실제 엔진명을 표시하기 위함). 알아내지 못하면 호출 안 함.
    private val onEngineLabelResolved: ((String) -> Unit)? = null,
) : SpeechEngine {
    private val mainHandler = Handler(Looper.getMainLooper())

    @Volatile
    private var ready = false

    // 기기 기본(null)이면 2-arg로 시스템 기본 엔진을 그대로 쓴다(targetSdk 34에선 삼성이 기본으로
    // 잡힌다). 특정 엔진을 고르면 3-arg로 그 엔진에 붙는다.
    private val tts: TextToSpeech =
        if (enginePackage != null) {
            TextToSpeech(context, ::onInit, enginePackage)
        } else {
            TextToSpeech(context, ::onInit)
        }

    private fun onInit(status: Int) {
        if (status != TextToSpeech.SUCCESS) return
        // OPicHelper(동작 확인된 사용자 앱)와 동일하게 setLanguage만 한다 — voice 오버라이드 없이.
        // 언어 데이터가 없으면 강제하지 않고 엔진 기본 언어에 맡긴다(무음보다 낫다).
        val langResult = tts.setLanguage(locale)
        if (langResult == TextToSpeech.LANG_MISSING_DATA || langResult == TextToSpeech.LANG_NOT_SUPPORTED) {
            tts.language = Locale.getDefault()
        }
        tts.setSpeechRate(rate)
        tts.setOnUtteranceProgressListener(progressListener)
        ready = true
        // 실제 사용 중인 엔진(기기 기본 선택 시 defaultEngine)의 표시 이름을 UI에 돌려준다.
        val activePkg = enginePackage ?: tts.defaultEngine
        tts.engines.firstOrNull { it.name == activePkg }?.label?.let { resolved ->
            mainHandler.post { onEngineLabelResolved?.invoke(resolved) }
        }
    }

    private val progressListener =
        object : UtteranceProgressListener() {
            override fun onStart(utteranceId: String?) = notify(true)

            override fun onDone(utteranceId: String?) = notify(false)

            @Deprecated("Deprecated in Java")
            override fun onError(utteranceId: String?) = notify(false)

            override fun onError(
                utteranceId: String?,
                errorCode: Int,
            ) = notify(false)

            override fun onStop(
                utteranceId: String?,
                interrupted: Boolean,
            ) = notify(false)

            private fun notify(speaking: Boolean) {
                mainHandler.post { onSpeakingChanged(speaking) }
            }
        }

    override fun speak(text: String) {
        if (!ready) return
        tts.speak(text, TextToSpeech.QUEUE_FLUSH, null, UTTERANCE_ID)
    }

    override fun stop() {
        tts.stop()
        onSpeakingChanged(false)
    }

    override fun release() {
        tts.stop()
        tts.shutdown()
    }

    private companion object {
        const val UTTERANCE_ID = "ddakpul-read"
    }
}
