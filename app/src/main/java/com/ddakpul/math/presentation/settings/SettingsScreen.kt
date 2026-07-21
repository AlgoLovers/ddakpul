package com.ddakpul.math.presentation.settings

import android.content.Intent
import android.os.Build
import android.provider.Settings
import android.speech.tts.TextToSpeech
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.ddakpul.math.BuildConfig
import com.ddakpul.math.R
import com.ddakpul.math.core.common.LocaleManagerCompat
import com.ddakpul.math.domain.model.SessionGoals
import com.ddakpul.math.presentation.common.ParentGateDialog
import com.ddakpul.math.presentation.common.SpeechSettings
import com.ddakpul.math.presentation.common.rememberSpeaker
import com.ddakpul.math.presentation.common.tts.DownloadState
import com.ddakpul.math.presentation.common.tts.TtsModel
import com.ddakpul.math.presentation.common.tts.TtsModels

@Composable
fun SettingsScreen(
    onOpenPrivacy: () -> Unit,
    modifier: Modifier = Modifier,
    viewModel: SettingsViewModel = hiltViewModel(),
) {
    var showResetDialog by remember { mutableStateOf(false) }
    var showResetGate by remember { mutableStateOf(false) }
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val pendingShareText by viewModel.pendingShareText.collectAsStateWithLifecycle()

    // 내보내기 텍스트가 준비되면 공유 시트를 띄운다(텔레그램 등 아무 앱으로나 전달 가능).
    val context = LocalContext.current
    LaunchedEffect(pendingShareText) {
        val text = pendingShareText ?: return@LaunchedEffect
        val sendIntent =
            Intent(Intent.ACTION_SEND).apply {
                type = "text/plain"
                putExtra(Intent.EXTRA_TEXT, text)
            }
        context.startActivity(Intent.createChooser(sendIntent, null))
        viewModel.consumeShareText()
    }

    Column(
        modifier = modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(24.dp),
        verticalArrangement = Arrangement.spacedBy(20.dp),
    ) {
        Text(
            text = stringResource(R.string.settings_title),
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
        )

        // 언어 — 앱 안에서 바로 한국어 ⇄ English. 문제 콘텐츠까지 바꾸려 앱을 재시작한다.
        LanguageCard()

        // 상위 난이도 열기 — 기본은 난이도 4단계까지, 켜면 5단계 이상 상위 문제도 추천에 나온다.
        UnlockLevelsCard(unlocked = uiState.unlockAllLevels, onToggle = viewModel::setUnlockAllLevels)

        // 하루 목표 — 아이가 스스로 정한다(자율성, SDT).
        DailyGoalCard(dailyGoal = uiState.dailyGoal, onSelect = viewModel::setDailyGoal)

        // 읽어주기(TTS) 음성 — 엔진·속도 선택. 받은 신경망 모델도 같은 목록에서 고른다.
        val neuralDownloaded by viewModel.ttsDownloaded.collectAsStateWithLifecycle()
        LaunchedEffect(Unit) { viewModel.refreshTtsDownloaded(TtsModels.SUPERTONIC) }
        val downloadedNeural = if (neuralDownloaded) TtsModels.ALL else emptyList()
        TtsCard(neuralModels = downloadedNeural, onDeleteNeural = viewModel::deleteTtsModel)

        // 고품질 신경망 음성 — 런타임 다운로드(선택). '받기 전'에만 보여 주는 획득용 카드다.
        // 받고 나면 이 카드는 사라지고, 위 '읽어주기 음성' 목록의 칩으로 선택/삭제한다.
        if (!neuralDownloaded) {
            NeuralVoiceCard(viewModel)
        }

        // 별로였던 문제 내보내기 — 부모가 개발 채널로 보내면 다음 업데이트에 반영된다.
        FeedbackExportCard(
            excludedCount = uiState.excludedCount,
            onShare = viewModel::requestExclusionShare,
        )

        ResetCard(onResetRequest = { showResetDialog = true })

        // 개인정보·데이터 안전 — 스토어 요건이자 신뢰 메시지.
        PrivacyCard(onOpenPrivacy = onOpenPrivacy)

        Text(
            // 버전 표기 — 어떤 빌드가 설치됐는지 확인용(업데이트 반영 여부 진단).
            text = stringResource(R.string.settings_about) + "  ·  v" + BuildConfig.VERSION_NAME + " (" + BuildConfig.VERSION_CODE + ")",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }

    if (showResetDialog) {
        ResetConfirmDialog(
            // 초기화는 되돌릴 수 없는 파괴적 동작 — 설명 후 부모 확인 게이트를 거친다.
            onConfirm = {
                showResetDialog = false
                showResetGate = true
            },
            onDismiss = { showResetDialog = false },
        )
    }
    if (showResetGate) {
        ParentGateDialog(
            onVerified = {
                viewModel.resetProgress()
                showResetGate = false
            },
            onDismiss = { showResetGate = false },
        )
    }
}

/** 상위 난이도(기본 상한 위, 5~) 열기 스위치 — 기본은 꺼짐(4단계까지). */
@Composable
private fun UnlockLevelsCard(
    unlocked: Boolean,
    onToggle: (Boolean) -> Unit,
) {
    SettingsCard(title = stringResource(R.string.settings_unlock_levels_title)) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text(
                text = stringResource(R.string.settings_unlock_levels_desc),
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.weight(1f).padding(end = 12.dp),
            )
            Switch(checked = unlocked, onCheckedChange = onToggle)
        }
    }
}

/**
 * 언어 토글 — 앱 안에서 한국어 ⇄ English 즉시 전환(시스템 언어 안 건드려도 됨).
 * 고르면 [LocaleManagerCompat.apply]가 선택을 저장하고 앱을 재시작해 UI 문자열은 물론
 * 문제 콘텐츠까지 새 언어로 다시 시딩되게 한다.
 */
@Composable
private fun LanguageCard() {
    val context = LocalContext.current
    val current = LocaleManagerCompat.currentLang(context)
    SettingsCard(title = stringResource(R.string.settings_language_title)) {
        Text(
            text = stringResource(R.string.settings_language_desc),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            FilterChip(
                selected = current == LocaleManagerCompat.KOREAN,
                onClick = { LocaleManagerCompat.apply(context, LocaleManagerCompat.KOREAN) },
                label = { Text(stringResource(R.string.settings_language_ko)) },
            )
            FilterChip(
                selected = current == LocaleManagerCompat.ENGLISH,
                onClick = { LocaleManagerCompat.apply(context, LocaleManagerCompat.ENGLISH) },
                label = { Text(stringResource(R.string.settings_language_en)) },
            )
        }
    }
}

@Composable
private fun PrivacyCard(onOpenPrivacy: () -> Unit) {
    SettingsCard(title = stringResource(R.string.settings_privacy_title)) {
        Text(
            text = stringResource(R.string.settings_privacy_desc),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        OutlinedButton(onClick = onOpenPrivacy) {
            Text(stringResource(R.string.settings_privacy_open))
        }
    }
}

@Composable
private fun DailyGoalCard(
    dailyGoal: Int,
    onSelect: (Int) -> Unit,
) {
    SettingsCard(title = stringResource(R.string.settings_goal_title)) {
        Text(
            text = stringResource(R.string.settings_goal_desc),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            SessionGoals.GOAL_OPTIONS.forEach { option ->
                FilterChip(
                    selected = dailyGoal == option,
                    onClick = { onSelect(option) },
                    label = { Text(stringResource(R.string.settings_goal_option, option)) },
                )
            }
        }
    }
}

/**
 * 고품질 신경망 음성(Supertonic) **획득용** 카드 — 모델(+.so) 다운로드와 진행률만 담당한다.
 * '받기 전'에만 보이고(부모가 `!downloaded`일 때만 렌더), 받고 나면 사라진다. 받은 뒤의 선택·
 * 삭제는 위 [TtsCard]의 칩/삭제 버튼으로 옮겼다 — 같은 음성을 두 군데서 관리하던 중복을 없앴다.
 */
@Composable
private fun NeuralVoiceCard(viewModel: SettingsViewModel) {
    val model = TtsModels.SUPERTONIC
    val downloadState by viewModel.ttsDownloadState.collectAsStateWithLifecycle()
    val sizeMb = (model.totalBytes / 1024 / 1024).toInt()

    SettingsCard(title = stringResource(model.displayNameRes)) {
        Text(
            text = stringResource(R.string.settings_neural_desc, sizeMb),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        val state = downloadState
        if (state is DownloadState.Downloading) {
            LinearProgressIndicator(
                progress = { state.percent / 100f },
                modifier = Modifier.fillMaxWidth(),
            )
            Text(
                text = stringResource(R.string.settings_neural_downloading, state.percent),
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        } else {
            if (state is DownloadState.Failed) {
                Text(
                    text = stringResource(R.string.settings_neural_failed, state.message),
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.error,
                )
            }
            Button(onClick = { viewModel.downloadTtsModel(model) }) {
                Text(stringResource(R.string.settings_neural_download, sizeMb))
            }
        }
    }
}

/**
 * 읽어주기 음성 설정 — 설치된 시스템 TTS 엔진 + 받아둔 신경망 모델을 **한 목록**에서 고른다.
 * 속도·미리 듣기(재생/정지 토글)·시스템 음성 설정 연결 포함.
 */
@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun TtsCard(
    neuralModels: List<TtsModel>,
    onDeleteNeural: (TtsModel) -> Unit,
) {
    val context = LocalContext.current
    var engines by remember { mutableStateOf<List<TextToSpeech.EngineInfo>>(emptyList()) }
    var defaultEngine by remember { mutableStateOf<String?>(null) }
    // 선택 상태는 SpeechSettings의 StateFlow를 관찰한다 — 탭하면 즉시 반영·미리듣기도 새 엔진.
    val selectedEngine by SpeechSettings.engine.collectAsStateWithLifecycle()
    val rate by SpeechSettings.rate.collectAsStateWithLifecycle()

    // 설치된 TTS 엔진 목록 + 기기 기본 엔진을 임시 인스턴스로 읽는다(getEngines가 반환하는 엔진).
    DisposableEffect(Unit) {
        var probe: TextToSpeech? = null
        probe =
            TextToSpeech(context) {
                engines = probe?.engines.orEmpty()
                defaultEngine = probe?.defaultEngine
            }
        onDispose { probe?.shutdown() }
    }
    val defaultLabel = engines.firstOrNull { it.name == defaultEngine }?.label
    // 미리 듣기용 — 선택이 바뀌면 새 엔진/속도로 즉시 다시 붙는다(SpeechSettings flow 구독).
    val speaker = rememberSpeaker()

    SettingsCard(title = stringResource(R.string.settings_tts_title)) {
        Text(
            text = stringResource(R.string.settings_tts_desc),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        if (engines.isNotEmpty()) {
            Text(stringResource(R.string.settings_tts_engine), style = MaterialTheme.typography.labelLarge)
            TtsEnginePicker(engines, defaultEngine, defaultLabel, selectedEngine, neuralModels)
        }
        // 지금 어떤 음성으로 읽는지 명확히 — 사용자 혼동 방지. 기기 기본이면 실제 엔진명을 쓴다.
        val activeLabel = if (selectedEngine == null) defaultLabel ?: speaker.engineLabel else speaker.engineLabel
        Text(
            text = stringResource(R.string.settings_tts_active, activeLabel),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.primary,
            fontWeight = FontWeight.Bold,
        )
        // 한국어 음성 안내 — 삼성은 안드로이드 15+에서 앱 사용이 막혀 Supertonic을 권한다.
        Text(
            text = stringResource(R.string.settings_tts_korean_tip),
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        // 받아둔 고품질 음성의 관리 — 선택 중이면 준비시간 안내, 그리고 삭제(용량 회수) 버튼.
        // 선택은 위 엔진 칩으로 하므로 여기엔 삭제만 둔다(별도 카드 없이 한곳에서 관리).
        neuralModels.forEach { m ->
            if (selectedEngine == TtsModels.engineValue(m)) {
                Text(
                    text = stringResource(R.string.settings_tts_neural_hint),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            TextButton(
                onClick = { onDeleteNeural(m) },
                contentPadding = PaddingValues(horizontal = 4.dp, vertical = 0.dp),
            ) {
                Text(
                    text = stringResource(R.string.settings_tts_neural_remove, (m.totalBytes / 1024 / 1024).toInt()),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        }
        Text(stringResource(R.string.settings_tts_speed), style = MaterialTheme.typography.labelLarge)
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            listOf(
                0.8f to R.string.settings_tts_slow,
                1.0f to R.string.settings_tts_normal,
                1.2f to R.string.settings_tts_fast,
            ).forEach { (r, res) ->
                FilterChip(
                    selected = rate == r,
                    onClick = { SpeechSettings.setRate(context, r) },
                    label = { Text(stringResource(res)) },
                )
            }
        }
        TtsPreviewRow(speaker = speaker, context = context)
    }
}

/** 시스템 TTS 엔진 + 받아둔 신경망 음성을 한 목록의 칩으로 고른다. */
@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun TtsEnginePicker(
    engines: List<TextToSpeech.EngineInfo>,
    defaultEngine: String?,
    defaultLabel: String?,
    selectedEngine: String?,
    neuralModels: List<TtsModel>,
) {
    val context = LocalContext.current
    // 줄바꿈으로 모든 엔진 칩을 한눈에(가로 스크롤에 숨지 않게).
    FlowRow(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        verticalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        FilterChip(
            selected = selectedEngine == null,
            onClick = { SpeechSettings.setEngine(context, null, null) },
            // '기기 기본' 워딩 대신 실제로 쓰는 엔진 이름을 그대로 보여준다("Google 음성
            // 인식 및 합성" 등). 이름이 아직 안 잡혔을 때만 중립 문구로 대체.
            label = { Text(defaultLabel ?: stringResource(R.string.settings_tts_engine_default)) },
        )
        // 기본 엔진과 같은 엔진은 명시 칩을 숨긴다(기본 칩과 중복 방지).
        engines.filter { it.name != defaultEngine }.forEach { e ->
            FilterChip(
                selected = selectedEngine == e.name,
                onClick = { SpeechSettings.setEngine(context, e.name, e.label) },
                label = { Text(e.label) },
            )
        }
        // 받아둔 신경망 음성(Supertonic 등)도 같은 목록에서 선택.
        neuralModels.forEach { m ->
            val value = TtsModels.engineValue(m)
            FilterChip(
                selected = selectedEngine == value,
                onClick = { SpeechSettings.setEngine(context, value, m.displayName(context)) },
                label = { Text(stringResource(m.displayNameRes)) },
            )
        }
    }
}

/** 미리 듣기(재생/정지 토글) + 시스템 음성 설정 바로가기. */
@Composable
private fun TtsPreviewRow(
    speaker: com.ddakpul.math.presentation.common.SpeakerController,
    context: android.content.Context,
) {
    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        // 미리 듣기 = 재생/정지 토글(재생 중 다시 누르면 멈춤).
        OutlinedButton(onClick = { speaker.toggle(context.getString(R.string.settings_tts_sample)) }) {
            Text(
                if (speaker.isSpeaking) {
                    stringResource(R.string.settings_tts_stop)
                } else {
                    stringResource(R.string.settings_tts_test)
                },
            )
        }
        TextButton(onClick = {
            runCatching {
                context.startActivity(
                    Intent("com.android.settings.TTS_SETTINGS").addFlags(Intent.FLAG_ACTIVITY_NEW_TASK),
                )
            }
        }) {
            Text(stringResource(R.string.settings_tts_system))
        }
    }
}

@Composable
private fun FeedbackExportCard(
    excludedCount: Int,
    onShare: () -> Unit,
) {
    SettingsCard(title = stringResource(R.string.settings_feedback_title)) {
        Text(
            text = stringResource(R.string.settings_feedback_desc),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        if (excludedCount > 0) {
            OutlinedButton(onClick = onShare) {
                Text(stringResource(R.string.settings_feedback_share, excludedCount))
            }
        } else {
            Text(
                text = stringResource(R.string.settings_feedback_empty),
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

@Composable
private fun ResetCard(onResetRequest: () -> Unit) {
    SettingsCard(title = stringResource(R.string.settings_reset)) {
        Text(
            text = stringResource(R.string.settings_reset_desc),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        OutlinedButton(onClick = onResetRequest) {
            Text(stringResource(R.string.settings_reset_confirm))
        }
    }
}

/** 설정 화면 공통 카드 틀 — 제목·설명·액션을 세로로 담는다. */
@Composable
private fun SettingsCard(
    title: String,
    content: @Composable androidx.compose.foundation.layout.ColumnScope.() -> Unit,
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceContainer),
    ) {
        Column(
            modifier = Modifier.fillMaxWidth().padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Text(text = title, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
            content()
        }
    }
}

@Composable
private fun ResetConfirmDialog(
    onConfirm: () -> Unit,
    onDismiss: () -> Unit,
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(stringResource(R.string.settings_reset_dialog_title)) },
        text = { Text(stringResource(R.string.settings_reset_dialog_body)) },
        confirmButton = {
            TextButton(onClick = onConfirm) {
                Text(stringResource(R.string.settings_reset_confirm))
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text(stringResource(R.string.settings_reset_cancel))
            }
        },
    )
}
