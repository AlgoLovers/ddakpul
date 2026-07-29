package com.ddakpul.math.presentation.solve

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.MoreHoriz
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.ddakpul.math.R
import com.ddakpul.math.core.designsystem.component.ChoiceOption
import com.ddakpul.math.core.designsystem.component.ChoiceState
import com.ddakpul.math.core.designsystem.component.GradientPrimaryButton
import com.ddakpul.math.core.designsystem.component.ProblemFigureView
import com.ddakpul.math.core.designsystem.component.ProgressDots
import com.ddakpul.math.domain.model.GradingResult
import com.ddakpul.math.domain.model.MathArea
import com.ddakpul.math.domain.model.Problem
import com.ddakpul.math.domain.model.SolutionVideo
import com.ddakpul.math.presentation.common.SpeakerController
import com.ddakpul.math.presentation.common.areaColor
import com.ddakpul.math.presentation.common.labelRes
import com.ddakpul.math.presentation.common.rememberSpeaker
import com.ddakpul.math.presentation.result.ResultSheet

@Composable
fun SolveScreen(
    onGoHome: () -> Unit,
    onWatchVideo: (SolutionVideo) -> Unit,
    modifier: Modifier = Modifier,
    onExitReview: (() -> Unit)? = null,
    viewModel: SolveViewModel = hiltViewModel(),
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    SolveContent(
        uiState = uiState,
        onSelect = viewModel::selectChoice,
        onSubmit = viewModel::submit,
        onNext = viewModel::loadNext,
        onExclude = viewModel::excludeCurrent,
        dissection =
            DissectionCallbacks(
                onTap = viewModel::tapDissectionCell,
                onSelectPiece = viewModel::selectDissectionPiece,
                onClear = viewModel::clearDissection,
                onSubmit = viewModel::submitDissection,
            ),
        onGoHome = onGoHome,
        onWatchVideo = onWatchVideo,
        onExitReview = onExitReview,
        modifier = modifier,
    )
}

@Composable
private fun SolveContent(
    uiState: SolveUiState,
    onSelect: (Int) -> Unit,
    onSubmit: () -> Unit,
    onNext: () -> Unit,
    onExclude: () -> Unit,
    dissection: DissectionCallbacks,
    onGoHome: () -> Unit,
    onWatchVideo: (SolutionVideo) -> Unit,
    onExitReview: (() -> Unit)?,
    modifier: Modifier = Modifier,
) {
    // 복습 모드에선 '다음 문제'(추천 흐름) 대신 오답 노트로 되돌아간다.
    val onPrimaryAdvance: () -> Unit = if (uiState.reviewMode) onExitReview ?: onNext else onNext
    var showExcludeDialog by remember { mutableStateOf(false) }
    // 연습장은 본문 폭 제한과 무관하게 콘텐츠 영역 전체를 덮어야 해, 상태를 여기(fillMaxSize Box)로 올려 오버레이로 띄운다.
    var showScratchpad by remember { mutableStateOf(false) }
    // 채점 시트 — 새 결과가 올 때마다 다시 연다. 내려도 하단 '결과 보기'로 다시 열 수 있다.
    var showResultSheet by remember(uiState.result) { mutableStateOf(true) }

    // 채점 순간 미세 촉각 피드백 — 답이 처리됐다는 확인일 뿐, 정오답에 따른 보상이 아니다
    // (과정 칭찬·물질 보상 금지 원칙, docs/PEDAGOGY.md). 정답/오답 같은 신호를 준다.
    val haptics = LocalHapticFeedback.current
    LaunchedEffect(uiState.result) {
        if (uiState.result != null) haptics.performHapticFeedback(HapticFeedbackType.LongPress)
    }

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

            // 풀이 중과 채점 후는 같은 화면 — 채점 후엔 보기 상태만 칠하고 위에 결과 시트를 올린다.
            SolvePhase.SOLVING, SolvePhase.GRADED -> {
                // 태블릿에서 한 줄이 지나치게 길어지지 않도록 콘텐츠 폭을 제한한다.
                if (uiState.isDissection) {
                    DissectionSolveBody(
                        uiState = uiState,
                        callbacks = dissection,
                        onNext = onPrimaryAdvance,
                        reviewMode = uiState.reviewMode,
                        modifier = Modifier.widthIn(max = CONTENT_MAX_WIDTH),
                    )
                } else {
                    SolvingBody(
                        uiState = uiState,
                        onSelect = onSelect,
                        onSubmit = onSubmit,
                        onExcludeRequest = { showExcludeDialog = true },
                        onScratchpad = { showScratchpad = true },
                        reviewMode = uiState.reviewMode,
                        onShowResult = { showResultSheet = true },
                        onAdvance = onPrimaryAdvance,
                        modifier = Modifier.widthIn(max = CONTENT_MAX_WIDTH),
                    )
                    uiState.result?.let { result ->
                        if (uiState.phase == SolvePhase.GRADED && showResultSheet) {
                            ResultSheet(
                                result = result,
                                showExplanation = uiState.showExplanation,
                                sessionStreak = uiState.sessionStreak,
                                softCutSuggested = uiState.softCutSuggested,
                                solutionVideo = uiState.solutionVideo,
                                retryLikely = uiState.retryLikely,
                                onDismiss = { showResultSheet = false },
                                onNext = onPrimaryAdvance,
                                onFinishToday = onGoHome,
                                onWatchVideo = onWatchVideo,
                                reviewMode = uiState.reviewMode,
                            )
                        }
                    }
                }
            }
        }

        // 연습장 오버레이 — 문제 풀이 위에 전체 폭으로 덮는다(도형 문제면 그림도 함께).
        uiState.problem?.let { problem ->
            if (showScratchpad) {
                ScratchpadOverlay(
                    statement = problem.statement,
                    figure = problem.figure,
                    strokes = rememberScratchStrokes(problem.id),
                    onDismiss = { showScratchpad = false },
                    modifier = Modifier.fillMaxSize(),
                )
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

/**
 * 문제풀기 리디자인(2026-07 시안) — 한 줄에 몰려 있던 6가지 정보를 3층으로 분리한다:
 * ① 진행 점 + ⋯ 메뉴 / ② 영역·난이도 칩 / ③ 하단 툴바(연습장·읽어주기·채점).
 * 채점하기는 스크롤과 무관하게 항상 손 닿는 곳(하단 고정)에 둔다.
 */
@Composable
private fun SolvingBody(
    uiState: SolveUiState,
    onSelect: (Int) -> Unit,
    onSubmit: () -> Unit,
    onExcludeRequest: () -> Unit,
    onScratchpad: () -> Unit,
    reviewMode: Boolean,
    modifier: Modifier = Modifier,
    onShowResult: (() -> Unit)? = null,
    onAdvance: (() -> Unit)? = null,
) {
    val problem = uiState.problem ?: return
    val result = uiState.result
    val speaker = rememberSpeaker()
    Column(modifier = modifier.fillMaxWidth().fillMaxHeight()) {
        SolveProgressRow(
            uiState = uiState,
            reviewMode = reviewMode,
            engineLabel = speaker.engineLabel,
            onExcludeRequest = onExcludeRequest,
        )
        SolveMetaRow(uiState = uiState, reviewMode = reviewMode)

        // 본문(문제 카드 + 보기)만 스크롤 — 툴바는 아래 고정.
        Column(
            modifier =
                Modifier
                    .weight(1f)
                    .verticalScroll(rememberScrollState())
                    .padding(horizontal = 20.dp, vertical = 12.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            ProblemCard(problem = problem)
            problem.choices.forEachIndexed { index, choice ->
                ChoiceOption(
                    index = index,
                    text = choice,
                    state = choiceStateFor(result = result, selectedIndex = uiState.selectedIndex, index = index),
                    onClick = { onSelect(index) },
                    enabled = result == null,
                )
            }
        }

        // ③ 하단 툴바 — 풀이 중엔 연습장·읽어주기+채점하기, 채점 후엔 결과 보기+다음.
        if (result == null) {
            SolveBottomBar(
                speaker = speaker,
                statement = problem.statement,
                canSubmit = uiState.canSubmit,
                onScratchpad = onScratchpad,
                onSubmit = onSubmit,
            )
        } else {
            GradedBottomBar(
                advanceLabel =
                    stringResource(if (reviewMode) R.string.review_back else R.string.result_next),
                onShowResult = onShowResult ?: {},
                onAdvance = onAdvance ?: {},
            )
        }
    }
}

/** ① 진행 점 줄 — 복습(오답 노트)엔 오늘 목표가 무의미해 점을 감춘다. */
@Composable
private fun SolveProgressRow(
    uiState: SolveUiState,
    reviewMode: Boolean,
    engineLabel: String,
    onExcludeRequest: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Row(
        modifier = modifier.fillMaxWidth().padding(start = 20.dp, end = 8.dp, top = 8.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        if (!reviewMode) {
            ProgressDots(
                solved = uiState.todaySolved,
                total = uiState.dailyGoal,
                highlightNext = true,
                height = 6.dp,
                modifier = Modifier.weight(1f),
            )
        } else {
            Spacer(modifier = Modifier.weight(1f))
        }
        SolveMoreMenu(
            engineLabel = engineLabel,
            showExclude = !reviewMode,
            onExcludeRequest = onExcludeRequest,
        )
    }
}

/** ② 메타 칩 줄 — 영역·난이도는 칩으로, 오른쪽엔 오늘 몇 번째 문제인지(복습이면 배지). */
@Composable
private fun SolveMetaRow(
    uiState: SolveUiState,
    reviewMode: Boolean,
    modifier: Modifier = Modifier,
) {
    val isReviewLabel = uiState.isReview || reviewMode
    Row(
        modifier = modifier.fillMaxWidth().padding(horizontal = 20.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        uiState.area?.let { AreaChip(area = it) }
        LevelChip(difficulty = uiState.difficulty)
        Spacer(modifier = Modifier.weight(1f))
        Text(
            text =
                if (isReviewLabel) {
                    stringResource(R.string.solve_review_badge)
                } else {
                    stringResource(R.string.solve_nth_problem, uiState.todaySolved + 1)
                },
            style = MaterialTheme.typography.bodyMedium,
            color =
                if (isReviewLabel) {
                    MaterialTheme.colorScheme.tertiary
                } else {
                    MaterialTheme.colorScheme.onSurfaceVariant
                },
            fontWeight = if (isReviewLabel) FontWeight.Bold else null,
        )
    }
}

/** 문제 카드 — 문장과 (있으면) 도형 그림. 그림이 문제의 절반이다. */
@Composable
private fun ProblemCard(
    problem: Problem,
    modifier: Modifier = Modifier,
) {
    Card(
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceContainer),
        modifier = modifier.fillMaxWidth(),
    ) {
        Text(
            text = problem.statement,
            style = MaterialTheme.typography.titleLarge,
            modifier = Modifier.fillMaxWidth().padding(24.dp),
        )
        problem.figure?.let { figure ->
            ProblemFigureView(figure = figure, modifier = Modifier.padding(bottom = 16.dp))
        }
    }
}

/** 보기 상태 — 채점 전엔 선택 여부, 채점 후엔 정답·오답·나머지 흐림. */
private fun choiceStateFor(
    result: GradingResult?,
    selectedIndex: Int?,
    index: Int,
): ChoiceState =
    when {
        result == null -> if (selectedIndex == index) ChoiceState.SELECTED else ChoiceState.DEFAULT
        index == result.correctIndex -> ChoiceState.CORRECT
        index == result.selectedIndex -> ChoiceState.WRONG_SELECTED
        else -> ChoiceState.DIMMED
    }

/** 채점 후 하단 바 — 시트를 내렸을 때도 결과 다시 보기와 다음 행동이 손에 남는다. */
@Composable
private fun GradedBottomBar(
    advanceLabel: String,
    onShowResult: () -> Unit,
    onAdvance: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Column(modifier = modifier.fillMaxWidth()) {
        HorizontalDivider(color = MaterialTheme.colorScheme.outlineVariant)
        Surface(color = MaterialTheme.colorScheme.surfaceContainer) {
            Row(
                modifier = Modifier.fillMaxWidth().padding(horizontal = 20.dp, vertical = 12.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(10.dp),
            ) {
                OutlinedButton(
                    onClick = onShowResult,
                    shape = RoundedCornerShape(18.dp),
                    modifier = Modifier.height(56.dp),
                ) {
                    Text(
                        text = stringResource(R.string.solve_show_result),
                        style = MaterialTheme.typography.titleSmall,
                    )
                }
                GradientPrimaryButton(onClick = onAdvance, modifier = Modifier.weight(1f)) {
                    Text(
                        text = advanceLabel,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                    )
                }
            }
        }
    }
}

/** ⋯ 메뉴 — '이 문제 별로예요'와 현재 읽어주기 음성 안내를 접어 둔다(본문 초점 유지). */
@Composable
private fun SolveMoreMenu(
    engineLabel: String,
    showExclude: Boolean,
    onExcludeRequest: () -> Unit,
) {
    var expanded by remember { mutableStateOf(false) }
    Box {
        IconButton(onClick = { expanded = true }) {
            Icon(
                imageVector = Icons.Filled.MoreHoriz,
                contentDescription = stringResource(R.string.solve_more_cd),
                tint = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
        DropdownMenu(expanded = expanded, onDismissRequest = { expanded = false }) {
            if (showExclude) {
                DropdownMenuItem(
                    text = { Text(stringResource(R.string.solve_exclude_button)) },
                    onClick = {
                        expanded = false
                        onExcludeRequest()
                    },
                )
            }
            // 어떤 음성으로 읽는지는 여기서 확인(사용자 혼동 방지) — 행동이 아니라 정보라 비활성.
            if (engineLabel.isNotBlank()) {
                DropdownMenuItem(
                    text = {
                        Text(
                            text = stringResource(R.string.solve_reading_with, engineLabel),
                            style = MaterialTheme.typography.labelMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    },
                    onClick = {},
                    enabled = false,
                )
            }
        }
    }
}

/** 영역 칩 — 영역 구분색 점 + 이름. 배경은 중립(役 기반), 색은 점에만 아껴 쓴다. */
@Composable
private fun AreaChip(
    area: MathArea,
    modifier: Modifier = Modifier,
) {
    Surface(
        modifier = modifier,
        color = MaterialTheme.colorScheme.surfaceContainerHigh,
        contentColor = MaterialTheme.colorScheme.onSurfaceVariant,
        shape = CircleShape,
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(6.dp),
        ) {
            Box(modifier = Modifier.size(7.dp).background(area.areaColor(), CircleShape))
            Text(
                text = stringResource(area.labelRes()),
                style = MaterialTheme.typography.labelLarge,
                fontWeight = FontWeight.SemiBold,
            )
        }
    }
}

/** 난이도 칩 — primaryContainer 짝으로 라이트/다크 자동 대응. */
@Composable
private fun LevelChip(
    difficulty: Int,
    modifier: Modifier = Modifier,
) {
    Surface(
        modifier = modifier,
        color = MaterialTheme.colorScheme.primaryContainer,
        contentColor = MaterialTheme.colorScheme.onPrimaryContainer,
        shape = CircleShape,
    ) {
        Text(
            text = stringResource(R.string.home_unit_level, difficulty),
            style = MaterialTheme.typography.labelLarge,
            fontWeight = FontWeight.Bold,
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
        )
    }
}

/** 하단 툴바 — 56dp 도구 버튼 2개 + 채점하기. 텍스트 버튼 말줄임 문제를 구조로 없앤다. */
@Composable
private fun SolveBottomBar(
    speaker: SpeakerController,
    statement: String,
    canSubmit: Boolean,
    onScratchpad: () -> Unit,
    onSubmit: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Column(modifier = modifier.fillMaxWidth()) {
        HorizontalDivider(color = MaterialTheme.colorScheme.outlineVariant)
        Surface(color = MaterialTheme.colorScheme.surfaceContainer) {
            Row(
                modifier = Modifier.fillMaxWidth().padding(horizontal = 20.dp, vertical = 12.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(10.dp),
            ) {
                SolveToolButton(
                    emoji = "✏️",
                    label = stringResource(R.string.solve_tool_scratchpad),
                    onClick = onScratchpad,
                )
                SolveToolButton(
                    emoji = if (speaker.isSpeaking) "⏹" else "🔊",
                    label =
                        stringResource(
                            if (speaker.isSpeaking) R.string.solve_tool_stop else R.string.solve_tool_read,
                        ),
                    onClick = { speaker.toggle(statement) },
                    active = speaker.isSpeaking,
                )
                GradientPrimaryButton(
                    onClick = onSubmit,
                    enabled = canSubmit,
                    modifier = Modifier.weight(1f),
                ) {
                    Text(
                        text = stringResource(R.string.solve_submit),
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                    )
                }
            }
        }
    }
}

/** 56dp 사각 도구 버튼 — 이모지 + 라벨 세로 스택. 재생 중이면 primary로 강조. */
@Composable
private fun SolveToolButton(
    emoji: String,
    label: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    active: Boolean = false,
) {
    Surface(
        onClick = onClick,
        modifier = modifier.size(56.dp),
        color = MaterialTheme.colorScheme.surfaceContainerHigh,
        contentColor =
            if (active) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurfaceVariant,
        shape = RoundedCornerShape(18.dp),
        border =
            BorderStroke(
                width = 1.dp,
                color =
                    if (active) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.outlineVariant,
            ),
    ) {
        Column(
            modifier = Modifier.fillMaxSize(),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center,
        ) {
            Text(text = emoji, style = MaterialTheme.typography.titleMedium)
            Text(
                text = label,
                style = MaterialTheme.typography.labelSmall,
                fontWeight = FontWeight.SemiBold,
                maxLines = 1,
            )
        }
    }
}

@Composable
private fun CenterMessage(content: @Composable () -> Unit) {
    Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) { content() }
}

private val CONTENT_MAX_WIDTH = 640.dp
