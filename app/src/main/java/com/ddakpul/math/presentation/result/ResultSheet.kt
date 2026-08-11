package com.ddakpul.math.presentation.result

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.stringArrayResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.ddakpul.math.R
import com.ddakpul.math.core.designsystem.component.GradientPrimaryButton
import com.ddakpul.math.domain.model.GradingResult
import com.ddakpul.math.domain.model.SolutionVideo

/** 이만큼 연속 정답이면 "연속 정답" 필과 칭찬 풀을 쓴다. */
private const val STREAK_PRAISE_THRESHOLD = 3

/**
 * 채점 결과 시트(2026-07 시안 03/04) — 화면을 갈아끼우지 않고 문제 위에 바텀시트로 올린다.
 * 방금 푼 문제가 뒤에 남아 맥락이 끊기지 않는다.
 * 정답: 축하 + 정답 행 + 연속 정답 필. 오답: 실패 배너 대신 중립 성장 프레이밍
 * (성장 마인드셋 원칙, docs/PEDAGOGY.md) + 내 답/정답 비교 + 오개념 카드.
 * 풀이/심화/영상은 세그먼트 탭 하나로 접는다.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ResultSheet(
    result: GradingResult,
    showExplanation: Boolean,
    sessionStreak: Int,
    softCutSuggested: Boolean,
    solutionVideo: SolutionVideo?,
    retryLikely: Boolean,
    goalJustReached: Boolean,
    onDismiss: () -> Unit,
    onNext: () -> Unit,
    onFinishToday: () -> Unit,
    onWatchVideo: (SolutionVideo) -> Unit,
    modifier: Modifier = Modifier,
    reviewMode: Boolean = false,
) {
    ModalBottomSheet(
        onDismissRequest = onDismiss,
        sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true),
        containerColor = MaterialTheme.colorScheme.surfaceContainer,
        modifier = modifier,
    ) {
        Column(
            modifier =
                Modifier
                    .fillMaxWidth()
                    .verticalScroll(rememberScrollState())
                    .padding(start = 22.dp, end = 22.dp, bottom = 24.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            ResultHeader(
                isCorrect = result.isCorrect,
                praise = praiseFor(result, sessionStreak, showExplanation),
            )

            val choices = result.problem.choices
            val selected = result.selectedIndex
            when {
                result.isCorrect -> {
                    CorrectAnswerRow(
                        answer = choices[result.correctIndex],
                        sessionStreak = sessionStreak,
                    )
                }

                // "모르겠어요"(무응답) — 고른 답이 없으니 비교 대신 정답만 보여준다.
                selected == null -> {
                    CorrectAnswerRow(
                        answer = choices[result.correctIndex],
                        sessionStreak = 0,
                    )
                }

                else -> {
                    AnswerCompareTiles(
                        myAnswer = choices[selected],
                        correctAnswer = choices[result.correctIndex],
                    )
                }
            }

            // 오개념 피드백(고른 오답에 맞는 설명이 있을 때)
            result.mistake?.let { mistake ->
                MistakeCard(body = mistake.misconception)
            }

            ExplanationTabs(result = result, solutionVideo = solutionVideo, onWatchVideo = onWatchVideo)

            if (showExplanation) {
                Text(
                    text = stringResource(R.string.result_remediation_hint),
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.primary,
                    fontWeight = FontWeight.Bold,
                )
            }

            // 하루 목표를 채운 순간은 아이에게 가장 큰 사건인데 아무 표시가 없었다.
            // 연출은 희소할수록 정보가 된다 — 목표를 막 채운 그 한 번만, 과장 없이 한 줄로.
            if (goalJustReached && !reviewMode) {
                GoalReachedCard()
            }
            // 세션 소프트 컷 — 목표 달성/집중 한계 도달 시 부드러운 종료 제안(강제 아님). 복습 모드엔 무의미해 감춘다.
            if (softCutSuggested && !reviewMode) {
                SoftCutCard()
            }

            ResultActions(
                result = result,
                retryLikely = retryLikely,
                reviewMode = reviewMode,
                onNext = onNext,
                onFinishToday = onFinishToday,
            )
        }
    }
}

/** 응원 메시지 — 과정(전략·시도)을 짚는 문구 풀에서 상황에 맞게 뽑는다. */
@Composable
private fun praiseFor(
    result: GradingResult,
    sessionStreak: Int,
    showExplanation: Boolean,
): String {
    val praisePool =
        when {
            result.isCorrect && sessionStreak >= STREAK_PRAISE_THRESHOLD -> {
                stringArrayResource(R.array.praise_streak)
            }

            result.isCorrect -> {
                stringArrayResource(R.array.praise_correct)
            }

            // "모르겠어요"로 풀이를 본 경우 — 틀림이 아니라 '막혔구나, 같이 보자' 격려 풀을 쓴다.
            result.selectedIndex == null -> {
                stringArrayResource(R.array.praise_stuck)
            }

            showExplanation -> {
                stringArrayResource(R.array.praise_stuck)
            }

            else -> {
                stringArrayResource(R.array.praise_wrong)
            }
        }
    return remember(result) { praisePool.random() }
}

/** 하단 행동 — 마치기(자율 종료)와 다음 문제. 복습 모드는 오답 노트 복귀 하나. */
@Composable
private fun ResultActions(
    result: GradingResult,
    retryLikely: Boolean,
    reviewMode: Boolean,
    onNext: () -> Unit,
    onFinishToday: () -> Unit,
) {
    if (reviewMode) {
        GradientPrimaryButton(onClick = onNext, modifier = Modifier.fillMaxWidth()) {
            Text(
                text = stringResource(R.string.review_back),
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
            )
        }
        return
    }
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(10.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        OutlinedButton(
            onClick = onFinishToday,
            shape = RoundedCornerShape(18.dp),
            // 고정 height는 글자 배율 2.0에서 라벨을 세로로 잘라먹는다.
            modifier = Modifier.heightIn(min = 56.dp),
        ) {
            Text(
                text = stringResource(R.string.result_finish),
                style = MaterialTheme.typography.titleSmall,
            )
        }
        GradientPrimaryButton(onClick = onNext, modifier = Modifier.weight(1f)) {
            // 규칙 7(오답 직후 재도전)이 이어질 상황이면 버튼이 스스로 무슨 일이 일어날지 말한다.
            if (!result.isCorrect && retryLikely) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(
                        text = stringResource(R.string.result_retry_cta),
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                    )
                    Text(
                        text = stringResource(R.string.result_retry_sub),
                        style = MaterialTheme.typography.labelSmall,
                    )
                }
            } else {
                Text(
                    text = stringResource(R.string.result_next),
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                )
            }
        }
    }
}

/**
 * 결과 헤더 — 정답은 축하, 오답은 "여기서 한 뼘 자라요" 중립 성장 프레이밍.
 * 코랄 실패 배너는 성장 마인드셋 문구와 모순이라 없앴다.
 */
@Composable
private fun ResultHeader(
    isCorrect: Boolean,
    praise: String,
) {
    val colors = MaterialTheme.colorScheme
    Row(
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        Box(
            modifier =
                Modifier
                    .size(56.dp)
                    .background(
                        color = if (isCorrect) colors.secondaryContainer else colors.primaryContainer,
                        shape = CircleShape,
                    ),
            contentAlignment = Alignment.Center,
        ) {
            Text(
                text = if (isCorrect) "✅" else "🧠",
                style = MaterialTheme.typography.headlineSmall,
            )
        }
        Column(verticalArrangement = Arrangement.spacedBy(3.dp)) {
            Text(
                text = stringResource(if (isCorrect) R.string.result_correct else R.string.result_grow_title),
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold,
                color = if (isCorrect) colors.onSecondaryContainer else colors.onSurface,
            )
            Text(
                text = praise,
                style = MaterialTheme.typography.bodyMedium,
                color = colors.onSurfaceVariant,
            )
        }
    }
}

/** 정답 행 — 정답 값과 (있으면) 연속 정답 필. */
@Composable
private fun CorrectAnswerRow(
    answer: String,
    sessionStreak: Int,
) {
    val colors = MaterialTheme.colorScheme
    Surface(
        color = colors.surfaceContainerHigh,
        shape = RoundedCornerShape(18.dp),
        modifier = Modifier.fillMaxWidth(),
    ) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 14.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Text(
                text = stringResource(R.string.result_answer_label),
                style = MaterialTheme.typography.labelLarge,
                color = colors.onSurfaceVariant,
            )
            Text(
                text = answer,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = colors.onSurface,
            )
            Spacer(modifier = Modifier.weight(1f))
            if (sessionStreak >= STREAK_PRAISE_THRESHOLD) {
                Surface(
                    color = colors.secondaryContainer,
                    contentColor = colors.onSecondaryContainer,
                    shape = CircleShape,
                ) {
                    Text(
                        text = stringResource(R.string.result_streak_pill, sessionStreak),
                        style = MaterialTheme.typography.labelMedium,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(horizontal = 11.dp, vertical = 6.dp),
                    )
                }
            }
        }
    }
}

/** 오답 비교 — 내 답과 정답을 나란히. 판정이 아니라 차이를 보여주는 게 목적. */
@Composable
private fun AnswerCompareTiles(
    myAnswer: String,
    correctAnswer: String,
) {
    val colors = MaterialTheme.colorScheme
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        AnswerTile(
            label = stringResource(R.string.result_my_answer_label),
            value = myAnswer,
            container = colors.errorContainer,
            content = colors.onErrorContainer,
            modifier = Modifier.weight(1f),
        )
        AnswerTile(
            label = stringResource(R.string.result_answer_label),
            value = correctAnswer,
            container = colors.secondaryContainer,
            content = colors.onSecondaryContainer,
            modifier = Modifier.weight(1f),
        )
    }
}

@Composable
private fun AnswerTile(
    label: String,
    value: String,
    container: Color,
    content: Color,
    modifier: Modifier = Modifier,
) {
    Surface(color = container, contentColor = content, shape = RoundedCornerShape(16.dp), modifier = modifier) {
        Column(
            modifier = Modifier.padding(horizontal = 14.dp, vertical = 13.dp),
            verticalArrangement = Arrangement.spacedBy(5.dp),
        ) {
            Text(text = label, style = MaterialTheme.typography.labelMedium)
            Text(text = value, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
        }
    }
}

/** 오개념 카드 — 고른 오답에 맞는 "이런 실수를 한 건 아닐까요?" 피드백. */
@Composable
private fun MistakeCard(body: String) {
    val colors = MaterialTheme.colorScheme
    Surface(
        color = colors.tertiaryContainer,
        contentColor = colors.onTertiaryContainer,
        shape = RoundedCornerShape(18.dp),
        modifier = Modifier.fillMaxWidth(),
    ) {
        Column(
            modifier = Modifier.fillMaxWidth().padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(6.dp),
        ) {
            Text(
                text = stringResource(R.string.result_mistake_label),
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.Bold,
            )
            Text(text = body, style = MaterialTheme.typography.bodyMedium)
        }
    }
}

private enum class ResultTab { EXPLANATION, DETAILED, VIDEO }

/**
 * 풀이/심화/영상 세그먼트 탭 — 세로로 쌓이던 버튼 3개를 탭 하나로 접는다.
 * 영상 탭은 내용이 아니라 행동(플레이어 이동)이라 선택 상태를 바꾸지 않는다.
 */
@Composable
private fun ExplanationTabs(
    result: GradingResult,
    solutionVideo: SolutionVideo?,
    onWatchVideo: (SolutionVideo) -> Unit,
) {
    val tabs =
        buildList {
            if (result.explanation != null) add(ResultTab.EXPLANATION)
            if (result.detailedExplanation != null) add(ResultTab.DETAILED)
            if (solutionVideo != null) add(ResultTab.VIDEO)
        }
    if (tabs.isEmpty()) return
    // 영상만 있는 경우엔 '선택된 탭'이 없다 — VIDEO는 본문이 없는 행동 탭이라
    // 선택 표시만 남고 아무것도 안 보이는 상태가 된다(2026-08 QA).
    var selected by remember(result) { mutableStateOf(tabs.firstOrNull { it != ResultTab.VIDEO }) }
    val colors = MaterialTheme.colorScheme
    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Row(
            modifier =
                Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(14.dp))
                    .background(colors.background)
                    .padding(4.dp),
            horizontalArrangement = Arrangement.spacedBy(4.dp),
        ) {
            tabs.forEach { tab ->
                ResultTabPill(
                    tab = tab,
                    isSelected = tab == selected,
                    onClick = {
                        if (tab == ResultTab.VIDEO) {
                            solutionVideo?.let(onWatchVideo)
                        } else {
                            selected = tab
                        }
                    },
                    modifier = Modifier.weight(1f),
                )
            }
        }
        val body =
            when (selected) {
                ResultTab.EXPLANATION -> result.explanation
                ResultTab.DETAILED -> result.detailedExplanation
                ResultTab.VIDEO, null -> null
            }
        body?.let {
            Text(text = it, style = MaterialTheme.typography.bodyLarge, color = colors.onSurface)
        }
    }
}

@Composable
private fun ResultTabPill(
    tab: ResultTab,
    isSelected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val colors = MaterialTheme.colorScheme
    Box(
        modifier =
            modifier
                .clip(RoundedCornerShape(11.dp))
                .background(if (isSelected) colors.surfaceContainerHigh else Color.Transparent)
                .clickable(onClick = onClick)
                // 탭 필도 손가락 타겟 — 9dp 패딩이면 38dp라 하드룰 6(48dp) 미달.
                .heightIn(min = 48.dp)
                .padding(vertical = 9.dp),
        contentAlignment = Alignment.Center,
    ) {
        Text(
            text = stringResource(tab.labelRes()),
            style = MaterialTheme.typography.labelLarge,
            fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Medium,
            color = if (isSelected) colors.onSurface else colors.onSurfaceVariant,
        )
    }
}

private fun ResultTab.labelRes(): Int =
    when (this) {
        ResultTab.EXPLANATION -> R.string.result_tab_explanation
        ResultTab.DETAILED -> R.string.result_tab_detailed
        ResultTab.VIDEO -> R.string.result_tab_video
    }

/** 오늘 목표를 방금 채웠을 때 한 번만 뜨는 축하 — 수집물·점수 없이 사실만 알린다. */
@Composable
private fun GoalReachedCard() {
    val colors = MaterialTheme.colorScheme
    Surface(
        color = colors.secondaryContainer,
        contentColor = colors.onSecondaryContainer,
        shape = RoundedCornerShape(18.dp),
        modifier = Modifier.fillMaxWidth(),
    ) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(16.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Text(text = "\uD83C\uDF89", style = MaterialTheme.typography.titleLarge)
            Text(
                text = stringResource(R.string.result_goal_reached),
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.Bold,
            )
        }
    }
}

/** 소프트 컷 안내 — 종료는 아래 '마치기' 버튼이 담당하므로 카드는 말만 건넨다. */
@Composable
private fun SoftCutCard() {
    val colors = MaterialTheme.colorScheme
    Surface(
        color = colors.tertiaryContainer,
        contentColor = colors.onTertiaryContainer,
        shape = RoundedCornerShape(18.dp),
        modifier = Modifier.fillMaxWidth(),
    ) {
        Column(
            modifier = Modifier.fillMaxWidth().padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(5.dp),
        ) {
            Text(
                text = stringResource(R.string.result_softcut_title),
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.Bold,
            )
            Text(
                text = stringResource(R.string.result_softcut_body),
                style = MaterialTheme.typography.bodyMedium,
            )
        }
    }
}
