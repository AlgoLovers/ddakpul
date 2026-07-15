package com.ddakpul.math.presentation.common

import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.Stable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import com.ddakpul.math.R
import com.ddakpul.math.presentation.common.tts.DirectTtsEngine
import com.ddakpul.math.presentation.common.tts.NeuralSpeechEngine
import com.ddakpul.math.presentation.common.tts.SpeechEngine
import com.ddakpul.math.presentation.common.tts.SystemSpeechEngine
import com.ddakpul.math.presentation.common.tts.TtsModels

/**
 * 읽어주기 컨트롤러 — 재생/정지 토글과 "지금 읽는 중" 상태, 현재 음성 이름을 들고 있다.
 * 화면은 이 객체만 보면 된다(엔진 종류에 독립적). [isSpeaking]·[engineLabel]은 관찰 가능한
 * Compose 상태라, 버튼 아이콘과 안내 문구가 실제 재생과 정확히 동기화된다.
 */
@Stable
class SpeakerController {
    /** 지금 읽어 주는 음성의 표시 이름("갤럭시 음성" 등) — 사용자가 어떤 TTS인지 명확히 알게. */
    var engineLabel by mutableStateOf("")
        internal set

    /** 현재 재생 중인지 — 토글 버튼 아이콘/문구와 동기화. */
    var isSpeaking by mutableStateOf(false)
        internal set

    private var engine: SpeechEngine? = null

    internal fun attach(newEngine: SpeechEngine) {
        engine = newEngine
    }

    internal fun detach() {
        engine = null
        isSpeaking = false
    }

    /** 재생 버튼의 기본 동작 — 읽는 중이면 멈추고, 아니면 읽는다(다시-처음-부터 방지). */
    fun toggle(text: String) {
        val current = engine ?: return
        if (isSpeaking) current.stop() else current.speak(text)
    }

    fun speak(text: String) {
        engine?.speak(text)
    }

    fun stop() {
        engine?.stop()
    }
}

/**
 * 문제를 소리 내어 읽어 주는 TTS 훅. 아직 글을 빠르게 못 읽는 저학년도 '읽기'가 아니라
 * '생각'에 집중하도록 돕는다(접근성). 화면을 벗어나면 엔진을 정리한다.
 *
 * [SpeechSettings]의 선택(엔진·속도)을 **관찰**한다 — 설정에서 삼성/구글 등 엔진이나 속도를
 * 바꾸면 즉시 새 엔진으로 다시 붙는다(예전의 "설정을 바꿔도 안 바뀌던" 버그 해결).
 */
@Composable
fun rememberSpeaker(): SpeakerController {
    val context = LocalContext.current
    LaunchedEffect(Unit) { SpeechSettings.load(context) }

    val enginePackage by SpeechSettings.engine.collectAsState()
    val rate by SpeechSettings.rate.collectAsState()
    val savedLabel by SpeechSettings.engineLabel.collectAsState()

    val defaultLabel = stringResource(R.string.settings_tts_engine_default)
    val label = savedLabel ?: defaultLabel

    // 선택값이 신경망 모델이고 실제로 받아져 있으면 신경망 엔진, 아니면 시스템 TTS.
    val neuralModel = TtsModels.neuralOf(enginePackage)?.takeIf { it.isDownloaded(context) }

    val controller = remember { SpeakerController() }
    controller.engineLabel = label

    // 명시적으로 고른 시스템 엔진(구글 아닌 삼성 등)은 표준 API가 getEngines() 필터로 못 붙이므로
    // 서비스에 직접 바인딩한다. '기기 기본'(null)은 안전한 SystemSpeechEngine 유지.
    val explicitSystemEngine = enginePackage?.takeUnless { TtsModels.neuralOf(it) != null }

    DisposableEffect(enginePackage, rate, label, neuralModel) {
        val onSpeaking = { speaking: Boolean -> controller.isSpeaking = speaking }
        val toDefault = { SpeechSettings.setEngine(context, null, null) }
        val engine: SpeechEngine =
            when {
                neuralModel != null -> {
                    NeuralSpeechEngine(
                        modelDir = neuralModel.dir(context),
                        soFile = neuralModel.soFile(context),
                        speed = rate,
                        label = label,
                        onSpeakingChanged = onSpeaking,
                        // 초기화 실패 시 선택을 기기 기본으로 되돌려 자동으로 시스템 음성 폴백.
                        onUnavailable = toDefault,
                    )
                }

                explicitSystemEngine != null -> {
                    DirectTtsEngine(
                        context = context,
                        enginePackage = explicitSystemEngine,
                        label = label,
                        onSpeakingChanged = onSpeaking,
                        // 직접 바인딩 실패 시 기기 기본으로 폴백.
                        onUnavailable = toDefault,
                    )
                }

                else -> {
                    SystemSpeechEngine(
                        context = context,
                        enginePackage = null,
                        rate = rate,
                        label = label,
                        onSpeakingChanged = onSpeaking,
                    )
                }
            }
        controller.attach(engine)
        onDispose {
            controller.detach()
            engine.release()
        }
    }
    return controller
}
