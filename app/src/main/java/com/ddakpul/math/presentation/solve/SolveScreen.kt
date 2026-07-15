package com.ddakpul.math.presentation.solve

import android.content.Context
import android.content.Intent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
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
import com.ddakpul.math.R
import com.ddakpul.math.core.designsystem.component.ChoiceOption
import com.ddakpul.math.core.designsystem.component.ChoiceState
import com.ddakpul.math.core.designsystem.component.ProblemFigureView
import com.ddakpul.math.domain.model.GradingResult
import com.ddakpul.math.presentation.common.labelRes
import com.ddakpul.math.presentation.common.rememberSpeaker
import com.ddakpul.math.presentation.result.ResultView

@Composable
fun SolveScreen(
    onGoHome: () -> Unit,
    onUpgrade: () -> Unit,
    modifier: Modifier = Modifier,
    viewModel: SolveViewModel = hiltViewModel(),
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val context = LocalContext.current
    SolveContent(
        uiState = uiState,
        onSelect = viewModel::selectChoice,
        onSubmit = viewModel::submit,
        onNext = viewModel::loadNext,
        onExclude = viewModel::excludeCurrent,
        onGoHome = onGoHome,
        onUpgrade = onUpgrade,
        onReportAnswer = { result -> shareAnswerReport(context, result) },
        modifier = modifier,
    )
}

/** '정답이 이상해요' — 문제 정보를 채운 쪽지를 공유 시트로 띄운다(개발자에게 전달, 무서버). */
private fun shareAnswerReport(
    context: Context,
    result: GradingResult,
) {
    val text =
        context.getString(
            R.string.report_answer_feedback,
            result.problem.id,
            result.problem.statement,
            result.problem.choices.joinToString(" / "),
            result.problem.choices[result.correctIndex],
            result.problem.choices[result.selectedIndex],
        )
    val sendIntent =
        Intent(Intent.ACTION_SEND).apply {
            type = "text/plain"
            putExtra(Intent.EXTRA_TEXT, text)
        }
    context.startActivity(Intent.createChooser(sendIntent, null))
}

@Composable
private fun SolveContent(
    uiState: SolveUiState,
    onSelect: (Int) -> Unit,
    onSubmit: () -> Unit,
    onNext: () -> Unit,
    onExclude: () -> Unit,
    onGoHome: () -> Unit,
    onUpgrade: () -> Unit,
    onReportAnswer: (GradingResult) -> Unit,
    modifier: Modifier = Modifier,
) {
    var showExcludeDialog by remember { mutableStateOf(false) }

    Box(modifier = modifier.fillMaxSize(), contentAlignment = Alignment.TopCenter) {
        when (uiState.phase) {
            SolvePhase.LOADING -> {
                CenterMessage { CircularProgressIndicator() }
            }

            SolvePhase.EMPTY -> {
                CenterMessage {
                    Text(stringResource(R.string.solve_empty), style = MaterialTheme.typography.bodyLarge)
                }
            }

            SolvePhase.SOLVING -> {
                // 태블릿에서 한 줄이 지나치게 길어지지 않도록 콘텐츠 폭을 제한한다.
                SolvingBody(
                    uiState = uiState,
                    onSelect = onSelect,
                    onSubmit = onSubmit,
                    onExcludeRequest = { showExcludeDialog = true },
                    onUpgrade = onUpgrade,
                    modifier = Modifier.widthIn(max = CONTENT_MAX_WIDTH),
                )
            }

            SolvePhase.GRADED -> {
                uiState.result?.let { result ->
                    ResultView(
                        result = result,
                        showExplanation = uiState.showExplanation,
                        sessionStreak = uiState.sessionStreak,
                        softCutSuggested = uiState.softCutSuggested,
                        isPremium = uiState.isPremium,
                        onNext = onNext,
                        onFinishToday = onGoHome,
                        onExcludeRequest = { showExcludeDialog = true },
                        onReportAnswer = { onReportAnswer(result) },
                        onUpgrade = onUpgrade,
                        modifier = Modifier.widthIn(max = CONTENT_MAX_WIDTH),
                    )
                }
            }
        }
    }

    if (showExcludeDialog) {
        ExcludeConfirmDialog(
            onConfirm = {
                showExcludeDialog = false
                onExclude()
            },
            onDismiss = { showExcludeDialog = false },
        )
    }
}

/** 제외 확인 다이얼로그 — 어렵다고 피하는 게 아니라 정말 별로인 문제만 표시하도록 한 번 확인한다. */
@Composable
private fun ExcludeConfirmDialog(
    onConfirm: () -> Unit,
    onDismiss: () -> Unit,
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(stringResource(R.string.solve_exclude_dialog_title)) },
        text = { Text(stringResource(R.string.solve_exclude_dialog_body)) },
        confirmButton = {
            TextButton(onClick = onConfirm) {
                Text(stringResource(R.string.solve_exclude_dialog_confirm))
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text(stringResource(R.string.solve_exclude_dialog_cancel))
            }
        },
    )
}

/** 읽어주기 버튼 + "지금 이 음성으로 읽어요" 표시. 재생 중 다시 누르면 정지(토글). */
@Composable
private fun ReadAloudButton(
    speaker: com.ddakpul.math.presentation.common.SpeakerController,
    text: String,
) {
    Column(horizontalAlignment = Alignment.End) {
        TextButton(onClick = { speaker.toggle(text) }) {
            Text(
                text =
                    if (speaker.isSpeaking) {
                        stringResource(R.string.solve_read_stop)
                    } else {
                        stringResource(R.string.solve_read_aloud)
                    },
            )
        }
        // 어떤 음성으로 읽는지 항상 보여준다(사용자 혼동 방지).
        if (speaker.engineLabel.isNotBlank()) {
            Text(
                text = stringResource(R.string.solve_reading_with, speaker.engineLabel),
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

@Composable
private fun SolvingBody(
    uiState: SolveUiState,
    onSelect: (Int) -> Unit,
    onSubmit: () -> Unit,
    onExcludeRequest: () -> Unit,
    onUpgrade: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val problem = uiState.problem ?: return
    val speaker = rememberSpeaker()
    Column(
        modifier = modifier.fillMaxWidth().verticalScroll(rememberScrollState()).padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        // 오늘의 목표 진행 — 근접 목표(proximal goal)가 유능감과 흥미를 만든다.
        TodayProgressHeader(todaySolved = uiState.todaySolved, dailyGoal = uiState.dailyGoal)

        // 무료 상한을 넘어 승급 준비가 됐으면 이용권을 권한다(계속 풀 수는 있다).
        if (uiState.premiumSuggested) {
            PremiumBanner(onUpgrade = onUpgrade)
        }

        // 무료 상한 난이도에 머물 때 — 왜 더 안 올라가는지 상시 안내(헷갈림 방지).
        if (uiState.showFreeCapHint) {
            FreeCapHint(onUpgrade = onUpgrade)
        }

        uiState.area?.let { area ->
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Row(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    if (uiState.isReview) {
                        Text(
                            text = stringResource(R.string.solve_review_badge),
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.tertiary,
                            fontWeight = FontWeight.Bold,
                        )
                    }
                    Text(
                        text = stringResource(R.string.solve_area_label, stringResource(area.labelRes()), uiState.difficulty),
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.primary,
                        fontWeight = FontWeight.Bold,
                    )
                }
                // 읽어주기 — 아직 글이 서툰 아이도 '생각'에 집중하도록. 재생 중 다시 누르면 정지.
                ReadAloudButton(speaker = speaker, text = problem.statement)
            }
        }

        Card(
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceContainer),
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(
                text = problem.statement,
                style = MaterialTheme.typography.titleLarge,
                modifier = Modifier.fillMaxWidth().padding(24.dp),
            )
            // 도형 지시서가 있으면 그림으로도 보여준다 — 그림이 문제의 절반이다.
            problem.figure?.let { figure ->
                ProblemFigureView(figure = figure, modifier = Modifier.padding(bottom = 16.dp))
            }
        }

        problem.choices.forEachIndexed { index, choice ->
            ChoiceOption(
                index = index,
                text = choice,
                state = if (uiState.selectedIndex == index) ChoiceState.SELECTED else ChoiceState.DEFAULT,
                onClick = { onSelect(index) },
                enabled = true,
            )
        }

        Button(
            onClick = onSubmit,
            enabled = uiState.canSubmit,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(
                text = stringResource(R.string.solve_submit),
                style = MaterialTheme.typography.titleMedium,
                modifier = Modifier.padding(vertical = 6.dp),
            )
        }

        // 문제 자체가 이상하거나 별로일 때의 탈출구 — 눈에 덜 띄게 맨 아래 작은 버튼으로 둔다.
        TextButton(
            onClick = onExcludeRequest,
            modifier = Modifier.align(Alignment.CenterHorizontally),
        ) {
            Text(
                text = stringResource(R.string.solve_exclude_button),
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

@Composable
private fun TodayProgressHeader(
    todaySolved: Int,
    dailyGoal: Int,
) {
    Column(verticalArrangement = Arrangement.spacedBy(6.dp), modifier = Modifier.fillMaxWidth()) {
        Text(
            text = stringResource(R.string.solve_today_progress, todaySolved, dailyGoal),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        LinearProgressIndicator(
            progress = { (todaySolved.toFloat() / dailyGoal).coerceIn(0f, 1f) },
            modifier = Modifier.fillMaxWidth(),
        )
    }
}

/** 무료 상한을 넘어 승급 준비가 됐을 때의 이용권 배너 — 막지 않고 권유만 한다. */
@Composable
private fun PremiumBanner(onUpgrade: () -> Unit) {
    Card(
        colors =
            CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.primaryContainer,
                contentColor = MaterialTheme.colorScheme.onPrimaryContainer,
            ),
        modifier = Modifier.fillMaxWidth(),
    ) {
        Column(
            modifier = Modifier.fillMaxWidth().padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Text(
                text = stringResource(R.string.solve_premium_banner),
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Bold,
            )
            Button(onClick = onUpgrade) {
                Text(stringResource(R.string.solve_premium_cta))
            }
        }
    }
}

/** 무료 상한 난이도에서 늘 보이는 저강도 안내 — 왜 난이도가 안 올라가는지 알려주고 페이월로 안내. */
@Composable
private fun FreeCapHint(onUpgrade: () -> Unit) {
    TextButton(
        onClick = onUpgrade,
        modifier = Modifier.fillMaxWidth(),
    ) {
        Text(
            text = stringResource(R.string.solve_free_cap_hint),
            style = MaterialTheme.typography.bodySmall,
        )
    }
}

@Composable
private fun CenterMessage(content: @Composable () -> Unit) {
    Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) { content() }
}

private val CONTENT_MAX_WIDTH = 640.dp
