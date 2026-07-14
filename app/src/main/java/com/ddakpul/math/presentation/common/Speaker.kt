package com.ddakpul.math.presentation.common

import android.speech.tts.TextToSpeech
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.platform.LocalContext
import java.util.Locale

/**
 * 문제를 소리 내어 읽어 주는 TTS 훅. 아직 글을 빠르게 못 읽는 저학년도 '읽기'가 아니라
 * '생각'에 집중하도록 돕는다(접근성). 화면을 벗어나면 엔진을 정리한다.
 *
 * [SpeechSettings]의 선택(엔진·속도)을 따른다 — 사용자가 설정에서 삼성/구글 등 엔진과
 * 말하기 속도를 고르면 여기에 반영된다(설정이 바뀌면 화면 재진입 시 새 엔진으로 다시 붙는다).
 * 반환값은 문자열을 읽는 함수 — 기기에 한국어 음성이 없으면 조용히 무시된다(크래시 없음).
 */
@Composable
fun rememberSpeaker(): (String) -> Unit {
    val context = LocalContext.current
    val enginePackage = SpeechSettings.enginePackage(context)
    val rate = SpeechSettings.rate(context)
    var engine by remember { mutableStateOf<TextToSpeech?>(null) }
    DisposableEffect(enginePackage, rate) {
        var tts: TextToSpeech? = null
        val onInit =
            TextToSpeech.OnInitListener { status ->
                if (status == TextToSpeech.SUCCESS) {
                    tts?.apply {
                        language = Locale.KOREAN
                        setSpeechRate(rate)
                        // 네트워크 없이 되는 한국어 음성을 우선(오프라인 원칙).
                        runCatching {
                            voices
                                ?.filter { it.locale.language == "ko" && !it.isNetworkConnectionRequired }
                                ?.maxByOrNull { it.quality }
                                ?.let { voice = it }
                        }
                    }
                }
            }
        tts =
            if (enginePackage != null) {
                TextToSpeech(context, onInit, enginePackage)
            } else {
                TextToSpeech(context, onInit)
            }
        engine = tts
        onDispose {
            tts?.stop()
            tts?.shutdown()
            engine = null
        }
    }
    return { text -> engine?.speak(text, TextToSpeech.QUEUE_FLUSH, null, "ddakpul-read") }
}
