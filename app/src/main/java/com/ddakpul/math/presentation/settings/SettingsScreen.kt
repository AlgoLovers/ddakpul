package com.ddakpul.math.presentation.settings

import android.content.Intent
import android.speech.tts.TextToSpeech
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
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
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.ddakpul.math.R
import com.ddakpul.math.domain.model.SessionGoals
import com.ddakpul.math.presentation.common.ParentGateDialog
import com.ddakpul.math.presentation.common.SpeechSettings
import com.ddakpul.math.presentation.common.launchFreeDeadlineText
import com.ddakpul.math.presentation.common.rememberSpeaker
import com.ddakpul.math.presentation.common.tts.DownloadState
import com.ddakpul.math.presentation.common.tts.TtsModel
import com.ddakpul.math.presentation.common.tts.TtsModels

@Composable
fun SettingsScreen(
    onOpenPaywall: () -> Unit,
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

        // 이용권 — 난이도 4~7과 전체 리포트를 여는 진입점. 현재 상태(무료/이용중)도 보여준다.
        PremiumCard(
            isPremium = uiState.isPremium,
            daysLeft = uiState.premiumDaysLeft,
            launchFreeUntilMillis = uiState.launchFreeUntilMillis,
            onOpenPaywall = onOpenPaywall,
        )

        // 하루 목표 — 아이가 스스로 정한다(자율성, SDT).
        DailyGoalCard(dailyGoal = uiState.dailyGoal, onSelect = viewModel::setDailyGoal)

        // 읽어주기(TTS) 음성 — 엔진·속도 선택. 받은 신경망 모델도 같은 목록에서 고른다.
        val neuralDownloaded by viewModel.ttsDownloaded.collectAsStateWithLifecycle()
        LaunchedEffect(Unit) { viewModel.refreshTtsDownloaded(TtsModels.SUPERTONIC) }
        val downloadedNeural = if (neuralDownloaded) TtsModels.ALL else emptyList()
        TtsCard(neuralModels = downloadedNeural)

        // 고품질 신경망 음성 — 런타임 다운로드(선택). 받은 뒤엔 위 '엔진'에서 골라 쓴다.
        NeuralVoiceCard(viewModel)

        // 별로였던 문제 내보내기 — 부모가 개발 채널로 보내면 다음 업데이트에 반영된다.
        FeedbackExportCard(
            excludedCount = uiState.excludedCount,
            onShare = viewModel::requestExclusionShare,
        )

        ResetCard(onResetRequest = { showResetDialog = true })

        // 개인정보·데이터 안전 — 스토어 요건이자 신뢰 메시지.
        PrivacyCard(onOpenPrivacy = onOpenPrivacy)

        Text(
            text = stringResource(R.string.settings_about),
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

@Composable
private fun PremiumCard(
    isPremium: Boolean,
    daysLeft: Int,
    launchFreeUntilMillis: Long,
    onOpenPaywall: () -> Unit,
) {
    val launchFree = !isPremium && launchFreeUntilMillis > 0L
    SettingsCard {
        Text(
            text = stringResource(R.string.settings_premium_title),
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
        )
        Text(
            text =
                when {
                    isPremium -> stringResource(R.string.settings_premium_active, daysLeft)
                    launchFree -> stringResource(R.string.settings_launch_free, launchFreeDeadlineText(launchFreeUntilMillis))
                    else -> stringResource(R.string.settings_premium_desc)
                },
            style = MaterialTheme.typography.bodyMedium,
            color =
                when {
                    isPremium -> MaterialTheme.colorScheme.primary
                    launchFree -> MaterialTheme.colorScheme.tertiary
                    else -> MaterialTheme.colorScheme.onSurfaceVariant
                },
        )
        OutlinedButton(onClick = onOpenPaywall) {
            Text(stringResource(if (isPremium) R.string.settings_premium_manage else R.string.settings_premium_open))
        }
    }
}

@Composable
private fun PrivacyCard(onOpenPrivacy: () -> Unit) {
    SettingsCard {
        Text(
            text = stringResource(R.string.settings_privacy_title),
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
        )
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
    SettingsCard {
        Text(
            text = stringResource(R.string.settings_goal_title),
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
        )
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

/** 고품질 신경망 음성(Supertonic) — 런타임 다운로드(모델+.so) + 진행률, 받으면 바로 선택 가능. */
@Composable
private fun NeuralVoiceCard(viewModel: SettingsViewModel) {
    val model = TtsModels.SUPERTONIC
    val downloadState by viewModel.ttsDownloadState.collectAsStateWithLifecycle()
    val downloaded by viewModel.ttsDownloaded.collectAsStateWithLifecycle()
    val sizeMb = (model.totalBytes / 1024 / 1024).toInt()
    LaunchedEffect(Unit) { viewModel.refreshTtsDownloaded(model) }

    SettingsCard {
        Text(
            text = model.displayName,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
        )
        Text(
            text = stringResource(R.string.settings_neural_desc, sizeMb),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        val state = downloadState
        when {
            state is DownloadState.Downloading -> {
                LinearProgressIndicator(
                    progress = { state.percent / 100f },
                    modifier = Modifier.fillMaxWidth(),
                )
                Text(
                    text = stringResource(R.string.settings_neural_downloading, state.percent),
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }

            downloaded -> {
                NeuralDownloadedActions(model = model, onDelete = { viewModel.deleteTtsModel(model) })
            }

            else -> {
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
}

/**
 * 받아둔 신경망 음성의 액션 — **받은 그 자리에서 바로 선택/해제**(엔진 목록까지 안 내려가도 됨).
 * 지금 이 음성으로 읽는 중이면 '사용 중'을 보여 주고, 아니면 '이 음성으로 읽기' 버튼을 준다.
 */
@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun NeuralDownloadedActions(
    model: TtsModel,
    onDelete: () -> Unit,
) {
    val context = LocalContext.current
    val selectedEngine by SpeechSettings.engine.collectAsStateWithLifecycle()
    val engineValue = TtsModels.engineValue(model)
    val isSelected = selectedEngine == engineValue

    Text(
        text = stringResource(R.string.settings_neural_done),
        style = MaterialTheme.typography.bodyMedium,
        color = MaterialTheme.colorScheme.primary,
    )
    if (isSelected) {
        Text(
            text = stringResource(R.string.settings_neural_inuse),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.primary,
            fontWeight = FontWeight.Bold,
        )
    }
    FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
        if (isSelected) {
            OutlinedButton(onClick = { SpeechSettings.setEngine(context, null, null) }) {
                Text(stringResource(R.string.settings_neural_use_default))
            }
        } else {
            Button(onClick = { SpeechSettings.setEngine(context, engineValue, model.displayName) }) {
                Text(stringResource(R.string.settings_neural_use))
            }
        }
        OutlinedButton(onClick = onDelete) {
            Text(stringResource(R.string.settings_neural_delete))
        }
    }
}

/**
 * 읽어주기 음성 설정 — 설치된 시스템 TTS 엔진 + 받아둔 신경망 모델을 **한 목록**에서 고른다.
 * 속도·미리 듣기(재생/정지 토글)·시스템 음성 설정 연결 포함.
 */
@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun TtsCard(neuralModels: List<TtsModel>) {
    val context = LocalContext.current
    var engines by remember { mutableStateOf<List<TextToSpeech.EngineInfo>>(emptyList()) }
    var defaultEngine by remember { mutableStateOf<String?>(null) }
    // 선택 상태는 SpeechSettings의 StateFlow를 관찰한다 — 탭하면 즉시 반영·미리듣기도 새 엔진.
    val selectedEngine by SpeechSettings.engine.collectAsStateWithLifecycle()
    val rate by SpeechSettings.rate.collectAsStateWithLifecycle()

    // 설치된 TTS 엔진 목록 + 기기 기본 엔진을 읽기 위한 임시 인스턴스.
    DisposableEffect(Unit) {
        var probe: TextToSpeech? = null
        probe =
            TextToSpeech(context) {
                engines = probe?.engines.orEmpty()
                defaultEngine = probe?.defaultEngine
            }
        onDispose { probe?.shutdown() }
    }
    // '기기 기본'이 실제로 어떤 엔진인지(중복 여부가 바로 보이게).
    val defaultLabel = engines.firstOrNull { it.name == defaultEngine }?.label
    // 미리 듣기용 — 선택이 바뀌면 새 엔진/속도로 즉시 다시 붙는다(SpeechSettings flow 구독).
    val speaker = rememberSpeaker()

    SettingsCard {
        Text(
            text = stringResource(R.string.settings_tts_title),
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
        )
        Text(
            text = stringResource(R.string.settings_tts_desc),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        if (engines.isNotEmpty()) {
            Text(stringResource(R.string.settings_tts_engine), style = MaterialTheme.typography.labelLarge)
            // 줄바꿈으로 모든 엔진 칩을 한눈에(가로 스크롤에 숨지 않게).
            FlowRow(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalArrangement = Arrangement.spacedBy(4.dp),
            ) {
                FilterChip(
                    selected = selectedEngine == null,
                    onClick = { SpeechSettings.setEngine(context, null, null) },
                    label = {
                        Text(
                            if (defaultLabel != null) {
                                stringResource(R.string.settings_tts_engine_default_named, defaultLabel)
                            } else {
                                stringResource(R.string.settings_tts_engine_default)
                            },
                        )
                    },
                )
                engines.forEach { e ->
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
                        onClick = { SpeechSettings.setEngine(context, value, m.displayName) },
                        label = { Text(m.displayName) },
                    )
                }
            }
        }
        // 지금 어떤 음성으로 읽는지 명확히 — 사용자 혼동 방지.
        Text(
            text = stringResource(R.string.settings_tts_active, speaker.engineLabel),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.primary,
            fontWeight = FontWeight.Bold,
        )
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
    SettingsCard {
        Text(
            text = stringResource(R.string.settings_feedback_title),
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
        )
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
    SettingsCard {
        Text(
            text = stringResource(R.string.settings_reset),
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
        )
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
private fun SettingsCard(content: @Composable androidx.compose.foundation.layout.ColumnScope.() -> Unit) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceContainer),
    ) {
        Column(
            modifier = Modifier.fillMaxWidth().padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
            content = content,
        )
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
