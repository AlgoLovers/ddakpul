package com.ddakpul.math.presentation.report

import androidx.compose.foundation.horizontalScroll
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
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Print
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.Icon
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringArrayResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.ddakpul.math.R
import com.ddakpul.math.core.designsystem.component.BarEntry
import com.ddakpul.math.core.designsystem.component.MasteryChip
import com.ddakpul.math.core.designsystem.component.MasteryMatrix
import com.ddakpul.math.core.designsystem.component.MasteryStage
import com.ddakpul.math.core.designsystem.component.MatrixEntry
import com.ddakpul.math.core.designsystem.component.MiniBarChart
import com.ddakpul.math.core.designsystem.component.SectionCard
import com.ddakpul.math.core.designsystem.component.StatTile
import com.ddakpul.math.core.designsystem.component.StepLineChart
import com.ddakpul.math.core.designsystem.component.TrendLineChart
import com.ddakpul.math.core.designsystem.component.masteryStageOf
import com.ddakpul.math.domain.model.ConceptStat
import com.ddakpul.math.domain.model.Difficulty
import com.ddakpul.math.domain.model.LearningStats
import com.ddakpul.math.domain.model.MathArea
import com.ddakpul.math.presentation.common.labelRes
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import kotlin.math.roundToInt

/** 숙달도 차트에 넣을 개념 수 상한 — 취약한 것부터 보여준다. */
private const val MAX_CONCEPT_ROWS = 6

/** 성장 곡선에 그릴 최근 시도 수 상한. */
private const val MAX_GROWTH_POINTS = 60

private val dayFormatter = DateTimeFormatter.ofPattern("M/d")

@Composable
fun ReportScreen(
    onPrintClick: () -> Unit,
    modifier: Modifier = Modifier,
    viewModel: ReportViewModel = hiltViewModel(),
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val stats = uiState.stats
    if (stats == null || stats.isEmpty) {
        Box(modifier = modifier.fillMaxSize().padding(24.dp), contentAlignment = Alignment.Center) {
            Text(
                text = stringResource(R.string.report_empty),
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
        return
    }
    ReportContent(
        stats = stats,
        dayCells = uiState.dayCells,
        insights = uiState.insights,
        weeklySummary = uiState.weeklySummary,
        masteryGrid = uiState.masteryGrid,
        onPrintClick = onPrintClick,
        modifier = modifier,
    )
}

@Composable
private fun ReportContent(
    stats: LearningStats,
    dayCells: List<DayCell>,
    insights: List<ReportInsight>,
    weeklySummary: WeeklySummary?,
    masteryGrid: List<MasteryCellUi>,
    onPrintClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Box(modifier = modifier.fillMaxSize(), contentAlignment = Alignment.TopCenter) {
        Column(
            modifier =
                Modifier
                    .widthIn(max = 720.dp)
                    .fillMaxWidth()
                    .verticalScroll(rememberScrollState())
                    .padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            Text(
                text = stringResource(R.string.report_title),
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold,
            )
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(
                    text = stringResource(R.string.report_subtitle),
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.weight(1f),
                )
                FilledTonalButton(onClick = onPrintClick) {
                    Icon(imageVector = Icons.Filled.Print, contentDescription = null)
                    Text(
                        text = stringResource(R.string.report_print_button),
                        modifier = Modifier.padding(start = 6.dp),
                    )
                }
            }

            SummaryTiles(stats)

            NarrativeSections(weeklySummary = weeklySummary, insights = insights)

            SectionCard(title = stringResource(R.string.report_daily_title)) {
                MiniBarChart(
                    entries = dayCells.map { BarEntry(value = it.solved.toFloat(), emphasized = it.isToday) },
                    startLabel = dayCells.firstOrNull()?.dateLabel().orEmpty(),
                    endLabel = dayCells.lastOrNull()?.dateLabel().orEmpty(),
                )
            }

            SectionCard(title = stringResource(R.string.report_trend_title)) {
                TrendLineChart(
                    values = dayCells.map { it.accuracy },
                    startLabel = dayCells.firstOrNull()?.dateLabel().orEmpty(),
                    endLabel = dayCells.lastOrNull()?.dateLabel().orEmpty(),
                )
            }

            if (stats.difficultyProgress.size >= 2) {
                SectionCard(title = stringResource(R.string.report_growth_title)) {
                    StepLineChart(
                        values = stats.difficultyProgress.takeLast(MAX_GROWTH_POINTS).map { it.difficulty },
                        minValue = Difficulty.MIN,
                        maxValue = Difficulty.MAX,
                    )
                    Text(
                        text = stringResource(R.string.report_growth_caption),
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
            }

            val concepts = stats.conceptStats.filter { it.solved >= 2 }.take(MAX_CONCEPT_ROWS)
            if (concepts.isNotEmpty()) {
                SectionCard(title = stringResource(R.string.report_concept_title)) {
                    concepts.forEach { concept -> ConceptRow(concept) }
                }
            }

            SectionCard(title = stringResource(R.string.report_matrix_title)) {
                MasteryMap(masteryGrid = masteryGrid, currentDifficulty = stats.currentDifficulty)
            }

            SectionCard(title = stringResource(R.string.report_parent_tips_title)) {
                stringArrayResource(R.array.parent_tips).forEach { tip ->
                    Text(
                        text = "• $tip",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
            }
        }
    }
}

@Composable
private fun SummaryTiles(stats: LearningStats) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        StatTile(
            label = stringResource(R.string.report_total_solved),
            value = stringResource(R.string.home_unit_count, stats.totalSolved),
            modifier = Modifier.weight(1f),
        )
        StatTile(
            label = stringResource(R.string.report_accuracy),
            value = stringResource(R.string.home_unit_percent, (stats.accuracy * 100).roundToInt()),
            modifier = Modifier.weight(1f),
        )
        StatTile(
            label = stringResource(R.string.report_current_level),
            value = stringResource(R.string.home_unit_level, stats.currentDifficulty),
            modifier = Modifier.weight(1f),
        )
        StatTile(
            label = stringResource(R.string.report_streak),
            value = stringResource(R.string.report_unit_days, stats.streakDays),
            modifier = Modifier.weight(1f),
        )
    }
}

/** 해석이 끝난 "말" 섹션 — 주간 요약 문단과 인사이트 목록. */
@Composable
private fun NarrativeSections(
    weeklySummary: WeeklySummary?,
    insights: List<ReportInsight>,
) {
    Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
        weeklySummary?.let { summary ->
            SectionCard(title = stringResource(R.string.report_weekly_title)) {
                Text(
                    text = summary.toParagraph(),
                    style = MaterialTheme.typography.bodyLarge,
                )
            }
        }

        if (insights.isNotEmpty()) {
            SectionCard(title = stringResource(R.string.report_insights_title)) {
                insights.forEach { insight ->
                    Text(
                        text = insight.toText(),
                        style = MaterialTheme.typography.bodyLarge,
                    )
                }
            }
        }
    }
}

/** 주간 요약을 자연스러운 한 문단으로 조립한다. */
@Composable
private fun WeeklySummary.toParagraph(): String {
    if (solved == 0) return stringResource(R.string.weekly_none)
    return buildString {
        append(stringResource(R.string.weekly_base, studyDays, solved, accuracyPercent))
        deltaPercentPoint?.let { delta ->
            if (delta > 0) {
                append(' ')
                append(stringResource(R.string.weekly_delta_up, delta))
            } else if (delta < 0) {
                append(' ')
                append(stringResource(R.string.weekly_delta_down, -delta))
            }
        }
        weakConcept?.let { concept ->
            append(' ')
            append(stringResource(R.string.weekly_weak, concept))
        }
    }
}

@Composable
private fun ReportInsight.toText(): String =
    when (this) {
        is ReportInsight.GoalDone -> stringResource(R.string.insight_goal_done)
        is ReportInsight.Streak -> stringResource(R.string.insight_streak, days)
        is ReportInsight.AccuracyUp -> stringResource(R.string.insight_accuracy_up, deltaPercentPoint)
        is ReportInsight.AccuracyDown -> stringResource(R.string.insight_accuracy_down, deltaPercentPoint)
        is ReportInsight.ErrorRecovery -> stringResource(R.string.insight_error_recovery, percent)
        is ReportInsight.WeakConcept -> stringResource(R.string.insight_weak_concept, concept, percent)
    }

private fun DayCell.dateLabel(): String = LocalDate.ofEpochDay(epochDay).format(dayFormatter)

@Composable
private fun ConceptRow(concept: ConceptStat) {
    Column(
        modifier = Modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(6.dp),
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                Text(
                    text = concept.concept,
                    style = MaterialTheme.typography.bodyLarge,
                    fontWeight = FontWeight.Bold,
                )
                MasteryChip(masteryStageOf(concept.solved, concept.accuracy))
            }
            Text(
                text =
                    stringResource(
                        R.string.report_concept_stat,
                        concept.solved,
                        (concept.accuracy * 100).roundToInt(),
                    ),
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
        LinearProgressIndicator(
            progress = { concept.accuracy },
            modifier = Modifier.fillMaxWidth(),
        )
    }
}

/**
 * 영역(행)×난이도(열) 숙달 지도. 학년 개념이 없는 이 앱에서 "어디까지 왔는지"를 보여주는
 * 유일한 좌표계라, 캡션으로 읽는 법을 먼저 짚고 범례로 색의 의미를 텍스트로도 밝힌다.
 */
@Composable
private fun MasteryMap(
    masteryGrid: List<MasteryCellUi>,
    currentDifficulty: Int,
) {
    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text(
            text = stringResource(R.string.report_matrix_caption),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        MasteryMatrix(
            rowLabels = MathArea.entries.map { stringResource(it.labelRes()) },
            columnLabels = (Difficulty.MIN..Difficulty.MAX).map { it.toString() },
            cells =
                masteryGrid.map { cell ->
                    MatrixEntry(
                        solved = cell.solved,
                        accuracy = cell.accuracy,
                        emphasized = cell.difficulty == currentDifficulty,
                    )
                },
        )
        Row(
            modifier = Modifier.horizontalScroll(rememberScrollState()),
            horizontalArrangement = Arrangement.spacedBy(6.dp),
        ) {
            MasteryStage.entries.forEach { stage -> MasteryChip(stage) }
        }
    }
}
