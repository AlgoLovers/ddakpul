package com.ddakpul.math.presentation.common.tts

import android.content.Context
import android.os.Handler
import android.os.Looper
import android.provider.Settings
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
    enginePackage: String?,
    private val rate: Float,
    override val label: String,
    private val onSpeakingChanged: (Boolean) -> Unit,
) : SpeechEngine {
    private val mainHandler = Handler(Looper.getMainLooper())

    @Volatile
    private var ready = false

    private val tts: TextToSpeech = createTts(context, enginePackage)

    /**
     * 사용자가 특정 엔진을 고르지 않았으면(기기 기본) 시스템 설정의 기본 TTS 엔진을 **직접 읽어**
     * 그 엔진으로 명시적으로 붙는다. 안드로이드 기본 생성자(TextToSpeech(context, listener))가
     * 시스템 기본(예: 삼성)을 무시하고 구글로 붙는 기기가 있어서, 시스템 설정값을 신뢰한다.
     */
    private fun createTts(
        context: Context,
        enginePackage: String?,
    ): TextToSpeech {
        val pkg = enginePackage ?: systemDefaultEngine(context)
        return if (pkg != null) {
            TextToSpeech(context, ::onInit, pkg)
        } else {
            TextToSpeech(context, ::onInit)
        }
    }

    /** 시스템 설정의 기본 TTS 엔진 패키지("tts_default_synth"). 없으면 null. */
    private fun systemDefaultEngine(context: Context): String? =
        runCatching {
            Settings.Secure.getString(context.contentResolver, "tts_default_synth")
        }.getOrNull()?.takeIf { it.isNotBlank() }

    private fun onInit(status: Int) {
        if (status != TextToSpeech.SUCCESS) return
        tts.language = Locale.KOREAN
        tts.setSpeechRate(rate)
        // 네트워크 없이 되는 한국어 음성을 우선(오프라인 원칙).
        runCatching {
            tts.voices
                ?.filter { it.locale.language == "ko" && !it.isNetworkConnectionRequired }
                ?.maxByOrNull { it.quality }
                ?.let { tts.voice = it }
        }
        tts.setOnUtteranceProgressListener(progressListener)
        ready = true
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
