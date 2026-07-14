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
 * 반환값은 문자열을 읽는 함수 — 기기에 한국어 음성이 없으면 조용히 무시된다(크래시 없음).
 */
@Composable
fun rememberSpeaker(): (String) -> Unit {
    val context = LocalContext.current
    var engine by remember { mutableStateOf<TextToSpeech?>(null) }
    DisposableEffect(context) {
        var tts: TextToSpeech? = null
        tts =
            TextToSpeech(context) { status ->
                if (status == TextToSpeech.SUCCESS) tts?.language = Locale.KOREAN
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
