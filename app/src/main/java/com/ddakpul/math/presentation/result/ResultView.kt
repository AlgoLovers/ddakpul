package com.ddakpul.math.presentation.result

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Lightbulb
import androidx.compose.material.icons.filled.PlayCircle
import androidx.compose.material.icons.filled.WarningAmber
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringArrayResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.ddakpul.math.R
import com.ddakpul.math.domain.model.GradingResult
import com.ddakpul.math.domain.model.SolutionVideo

/** 이만큼 연속 정답이면 "연속 정답" 칭찬 풀에서 뽑는다. */
private const val STREAK_PRAISE_THRESHOLD = 3

/**
 * 채점 결과 화면. 정답/오답 배너와 과정 칭찬 응원, 내가 고른 답과 정답,
 * (있으면) 오개념 피드백과 해설을 보여준다.
 * [showExplanation]이 true면(정체 감지) 기초부터 다시 하자는 안내를 강조한다.
 * [onExcludeRequest]는 "이 문제 별로예요" — 문제 자체에 대한 피드백 탈출구다.
 */
@Composable
fun ResultView(
    result: GradingResult,
    showExplanation: Boolean,
    sessionStreak: Int,
    softCutSuggested: Boolean,
    isPremium: Boolean,
    solutionVideo: SolutionVideo?,
    onNext: () -> Unit,
    onFinishToday: () -> Unit,
    onExcludeRequest: () -> Unit,
    onReportAnswer: () -> Unit,
    onUpgrade: () -> Unit,
    onWatchVideo: (SolutionVideo) -> Unit,
    modifier: Modifier = Modifier,
) {
    val colors = MaterialTheme.colorScheme
    Column(
        modifier = modifier.fillMaxWidth().verticalScroll(rememberScrollState()).padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        // 응원 메시지 — 과정(전략·시도)을 짚는 문구 풀에서 상황에 맞게 뽑는다.
        val praisePool =
            when {
                result.isCorrect && sessionStreak >= STREAK_PRAISE_THRESHOLD -> {
                    stringArrayResource(R.array.praise_streak)
                }

                result.isCorrect -> {
                    stringArrayResource(R.array.praise_correct)
                }

                showExplanation -> {
                    stringArrayResource(R.array.praise_stuck)
                }

                else -> {
                    stringArrayResource(R.array.praise_wrong)
                }
            }
        val praise = remember(result) { praisePool.random() }

        ResultBanner(isCorrect = result.isCorrect, praise = praise)

        val choices = result.problem.choices
        Text(
            text = stringResource(R.string.result_correct_answer, choices[result.correctIndex]),
            style = MaterialTheme.typography.bodyLarge,
            fontWeight = FontWeight.Bold,
        )
        if (!result.isCorrect) {
            Text(
                text = stringResource(R.string.result_your_answer, choices[result.selectedIndex]),
                style = MaterialTheme.typography.bodyMedium,
                color = colors.onSurfaceVariant,
            )
        }

        // 오개념 피드백(고른 오답에 맞는 설명이 있을 때)
        result.mistake?.let { mistake ->
            FeedbackCard(
                icon = Icons.Filled.WarningAmber,
                container = colors.tertiaryContainer,
                content = colors.onTertiaryContainer,
                label = stringResource(R.string.result_mistake_label),
                body = mistake.misconception,
            )
        }

        // 동영상 풀이 — 이 방법에 준비된 해설 영상이 있을 때만. 문자 해설보다 먼저 권한다(직관적).
        if (solutionVideo != null) {
            WatchVideoButton(onClick = { onWatchVideo(solutionVideo) })
        }

        // 1차 풀이 — 오답이면 바로 펼쳐 교정 학습을 돕고, 정답이면 '풀이 보기'로 원할 때 펼친다.
        ExplanationSection(result = result)

        // 2차(심화) 풀이 — 이용권 전용. 무료는 잠긴 티저로 안내.
        DetailedExplanationSection(result = result, isPremium = isPremium, onUpgrade = onUpgrade)

        if (showExplanation) {
            Text(
                text = stringResource(R.string.result_remediation_hint),
                style = MaterialTheme.typography.bodyMedium,
                color = colors.primary,
                fontWeight = FontWeight.Bold,
            )
        }

        // 세션 소프트 컷 — 목표 달성/집중 한계 도달 시 부드러운 종료 제안(강제 아님).
        if (softCutSuggested) {
            SoftCutCard(onFinishToday = onFinishToday)
        }

        Button(
            onClick = onNext,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(
                text = stringResource(R.string.result_next),
                style = MaterialTheme.typography.titleMedium,
                modifier = Modifier.padding(vertical = 6.dp),
            )
        }

        // 정답이 이상하다고 느끼면 개발자에게 바로 신고(문제 정보 자동 첨부) — 나도 틀릴 수 있으니.
        TextButton(
            onClick = onReportAnswer,
            modifier = Modifier.align(Alignment.CenterHorizontally),
        ) {
            Text(
                text = stringResource(R.string.report_answer_button),
                style = MaterialTheme.typography.bodySmall,
                color = colors.onSurfaceVariant,
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
                color = colors.onSurfaceVariant,
            )
        }
    }
}

/** '동영상 풀이 보기' 버튼 — 해당 방법에 영상이 준비된 문제에서만 보인다. */
@Composable
private fun WatchVideoButton(onClick: () -> Unit) {
    OutlinedButton(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth(),
    ) {
        Icon(
            imageVector = Icons.Filled.PlayCircle,
            contentDescription = null,
            modifier = Modifier.padding(end = 8.dp),
        )
        Text(stringResource(R.string.result_watch_video))
    }
}

/** 단계별 풀이. 오답이면 바로 펼치고(교정 학습), 정답이면 '풀이 보기'로 접어 둔다. */
@Composable
private fun ExplanationSection(result: GradingResult) {
    val explanation = result.explanation ?: return
    val colors = MaterialTheme.colorScheme
    var expanded by remember(result) { mutableStateOf(!result.isCorrect) }
    if (expanded) {
        FeedbackCard(
            icon = Icons.Filled.Lightbulb,
            container = colors.surfaceContainerHigh,
            content = colors.onSurface,
            label = stringResource(R.string.result_explanation_label),
            body = explanation,
        )
    } else {
        OutlinedButton(onClick = { expanded = true }) {
            Icon(
                imageVector = Icons.Filled.Lightbulb,
                contentDescription = null,
                modifier = Modifier.padding(end = 8.dp),
            )
            Text(stringResource(R.string.result_show_explanation))
        }
    }
}

/** 2차(심화) 풀이. 이용권 회원은 '심화 풀이 보기'로 펼치고, 무료 회원은 잠긴 티저 + 이용권 유도. */
@Composable
private fun DetailedExplanationSection(
    result: GradingResult,
    isPremium: Boolean,
    onUpgrade: () -> Unit,
) {
    val detailed = result.detailedExplanation ?: return
    val colors = MaterialTheme.colorScheme
    if (isPremium) {
        var expanded by remember(result) { mutableStateOf(false) }
        if (expanded) {
            FeedbackCard(
                icon = Icons.Filled.Lightbulb,
                container = colors.primaryContainer,
                content = colors.onPrimaryContainer,
                label = stringResource(R.string.result_detailed_label),
                body = detailed,
            )
        } else {
            OutlinedButton(onClick = { expanded = true }) {
                Icon(
                    imageVector = Icons.Filled.Lightbulb,
                    contentDescription = null,
                    modifier = Modifier.padding(end = 8.dp),
                )
                Text(stringResource(R.string.result_detailed_show))
            }
        }
    } else {
        Card(
            colors =
                CardDefaults.cardColors(
                    containerColor = colors.primaryContainer,
                    contentColor = colors.onPrimaryContainer,
                ),
            modifier = Modifier.fillMaxWidth(),
        ) {
            Column(
                modifier = Modifier.fillMaxWidth().padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                Text(
                    text = stringResource(R.string.result_detailed_locked_title),
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                )
                Text(
                    text = stringResource(R.string.result_detailed_locked_body),
                    style = MaterialTheme.typography.bodyMedium,
                )
                OutlinedButton(onClick = onUpgrade) {
                    Text(stringResource(R.string.result_detailed_cta))
                }
            }
        }
    }
}

@Composable
private fun SoftCutCard(onFinishToday: () -> Unit) {
    val colors = MaterialTheme.colorScheme
    Card(
        colors =
            CardDefaults.cardColors(
                containerColor = colors.tertiaryContainer,
                contentColor = colors.onTertiaryContainer,
            ),
        modifier = Modifier.fillMaxWidth(),
    ) {
        Column(
            modifier = Modifier.fillMaxWidth().padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Text(
                text = stringResource(R.string.result_softcut_title),
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
            )
            Text(
                text = stringResource(R.string.result_softcut_body),
                style = MaterialTheme.typography.bodyMedium,
            )
            OutlinedButton(onClick = onFinishToday) {
                Text(stringResource(R.string.result_softcut_stop))
            }
        }
    }
}

/** 정답/오답 배너 + 과정 칭찬 응원 한 줄. */
@Composable
private fun ResultBanner(
    isCorrect: Boolean,
    praise: String,
) {
    val colors = MaterialTheme.colorScheme
    Card(
        colors =
            CardDefaults.cardColors(
                containerColor = if (isCorrect) colors.secondaryContainer else colors.errorContainer,
                contentColor = if (isCorrect) colors.onSecondaryContainer else colors.onErrorContainer,
            ),
        modifier = Modifier.fillMaxWidth(),
    ) {
        Column(
            modifier = Modifier.fillMaxWidth().padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                Icon(
                    imageVector = if (isCorrect) Icons.Filled.CheckCircle else Icons.Filled.WarningAmber,
                    contentDescription = null,
                )
                Text(
                    text = stringResource(if (isCorrect) R.string.result_correct else R.string.result_wrong),
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold,
                )
            }
            Text(
                text = praise,
                style = MaterialTheme.typography.bodyLarge,
            )
        }
    }
}

@Composable
private fun FeedbackCard(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    container: androidx.compose.ui.graphics.Color,
    content: androidx.compose.ui.graphics.Color,
    label: String,
    body: String,
) {
    Card(
        colors = CardDefaults.cardColors(containerColor = container, contentColor = content),
        modifier = Modifier.fillMaxWidth(),
    ) {
        Column(
            modifier = Modifier.fillMaxWidth().padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                Icon(imageVector = icon, contentDescription = null)
                Text(text = label, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
            }
            Text(text = body, style = MaterialTheme.typography.bodyMedium)
        }
    }
}
