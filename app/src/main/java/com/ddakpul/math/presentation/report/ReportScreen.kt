package com.ddakpul.math.presentation.report

import android.content.Context
import android.print.PrintAttributes
import android.print.PrintManager
import androidx.compose.foundation.background
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Print
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringArrayResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.ddakpul.math.R
import com.ddakpul.math.core.common.toPercentInt
import com.ddakpul.math.core.designsystem.component.BarEntry
import com.ddakpul.math.core.designsystem.component.LevelTrack
import com.ddakpul.math.core.designsystem.component.MasteryChip
import com.ddakpul.math.core.designsystem.component.MasteryMatrix
import com.ddakpul.math.core.designsystem.component.MasteryStage
import com.ddakpul.math.core.designsystem.component.MatrixEntry
import com.ddakpul.math.core.designsystem.component.MiniBarChart
import com.ddakpul.math.core.designsystem.component.ProblemFigureView
import com.ddakpul.math.core.designsystem.component.ProgressBar
import com.ddakpul.math.core.designsystem.component.SectionCard
import com.ddakpul.math.core.designsystem.component.StatTile
import com.ddakpul.math.core.designsystem.component.StepLineChart
import com.ddakpul.math.core.designsystem.component.TrendLineChart
import com.ddakpul.math.core.designsystem.component.masteryStageOf
import com.ddakpul.math.core.designsystem.theme.AreaChange
import com.ddakpul.math.core.designsystem.theme.AreaData
import com.ddakpul.math.core.designsystem.theme.AreaNumber
import com.ddakpul.math.core.designsystem.theme.AreaShape
import com.ddakpul.math.domain.model.AreaStat
import com.ddakpul.math.domain.model.ConceptStat
import com.ddakpul.math.domain.model.Difficulty
import com.ddakpul.math.domain.model.LearningStats
import com.ddakpul.math.domain.model.MathArea
import com.ddakpul.math.domain.model.NextStep
import com.ddakpul.math.domain.model.Problem
import com.ddakpul.math.presentation.common.labelRes
import com.ddakpul.math.presentation.print.ReportPdfGenerator
import com.ddakpul.math.presentation.print.ReportTexts
import com.ddakpul.math.presentation.print.WorksheetPrintAdapter
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import kotlin.math.roundToInt

/** 숙달도 차트에 넣을 개념 수 상한 — 취약한 것부터 보여준다. */
private const val MAX_CONCEPT_ROWS = 6

/** 성장 곡선에 그릴 최근 시도 수 상한. */
private const val MAX_GROWTH_POINTS = 60

private val dayFormatter = DateTimeFormatter.ofPattern("M/d")

/** 리포트 PDF 상단의 '기준일' 표기. */
private val exportDateFormatter = DateTimeFormatter.ofPattern("yyyy. M. d.")

// modifier가 두 번 쓰이지만 빈 상태 Column과 ReportContent는 상호배타 분기(early return)라 한 번만 적용된다.
@Suppress("ComposeModifierReused")
@Composable
fun ReportScreen(
    onPrintClick: () -> Unit,
    onStartSolving: () -> Unit,
    modifier: Modifier = Modifier,
    viewModel: ReportViewModel = hiltViewModel(),
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val stats = uiState.stats
    if (stats == null || stats.isEmpty) {
        Column(
            modifier = modifier.fillMaxSize().padding(32.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(14.dp, Alignment.CenterVertically),
        ) {
            Text(text = "📊", style = MaterialTheme.typography.displayMedium)
            Text(
                text = stringResource(R.string.report_empty),
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center,
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
        nextStep = uiState.nextStep,
        onPrintClick = onPrintClick,
        onStartSolving = onStartSolving,
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
    nextStep: NextStep?,
    onPrintClick: () -> Unit,
    onStartSolving: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    val reportTexts = rememberReportTexts(stats)
    val exportJobName = stringResource(R.string.report_export_job)
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
            // 제목과 인쇄 버튼을 한 줄에(짧은 제목 옆이라 폰에서도 버튼이 안 눌린다), 부제는 아래 전체폭.
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(
                    text = stringResource(R.string.report_title),
                    style = MaterialTheme.typography.headlineMedium,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.weight(1f, fill = false),
                )
                FilledTonalButton(onClick = onPrintClick) {
                    Icon(imageVector = Icons.Filled.Print, contentDescription = null)
                    Text(
                        text = stringResource(R.string.report_print_button),
                        modifier = Modifier.padding(start = 6.dp),
                    )
                }
            }
            Text(
                text = stringResource(R.string.report_subtitle),
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )

            HeroCard(stats)

            nextStep?.let { NextStepCard(it, onStartSolving) }

            KeyStatTiles(stats)

            if (stats.areaStats.any { it.solved > 0 }) {
                SectionCard(
                    title = stringResource(R.string.report_area_title),
                    icon = "🧭",
                    subtitle = stringResource(R.string.report_area_subtitle),
                ) {
                    AreaBreakdown(stats.areaStats)
                }
            }

            NarrativeSections(weeklySummary = weeklySummary, insights = insights)

            // 오답 노트 — 최근 틀린 문제 + 풀이. 무료 포함 모두에게(오답 복습은 학습의 핵심).
            if (stats.recentMistakes.isNotEmpty()) {
                MistakeNoteSection(mistakes = stats.recentMistakes)
            }

            // 심화 분석(정답률 추이·성장 곡선·개념별 숙달·난이도별 숙달 지도).
            PremiumAnalyticsSections(stats = stats, dayCells = dayCells, masteryGrid = masteryGrid)

            SectionCard(title = stringResource(R.string.report_parent_tips_title), icon = "🧑‍🏫") {
                stringArrayResource(R.array.parent_tips).forEach { tip ->
                    Text(
                        text = "• $tip",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
            }

            // 이 리포트 자체를 한 장 PDF로 — 시스템 인쇄 대화상자의 'PDF로 저장'으로 보관/전달.
            OutlinedButton(
                onClick = { printReport(context, stats, reportTexts, exportJobName) },
                modifier = Modifier.fillMaxWidth(),
            ) {
                Icon(imageVector = Icons.Filled.Print, contentDescription = null)
                Text(
                    text = stringResource(R.string.report_export_button),
                    modifier = Modifier.padding(start = 6.dp),
                )
            }
        }
    }
}

/** 화면의 리소스 문자열을 모아 순수 [ReportTexts]로 만든다(생성기는 리소스에 접근하지 않는다). */
@Composable
private fun rememberReportTexts(stats: LearningStats): ReportTexts {
    val areaLabels = MathArea.entries.associateWith { stringResource(it.labelRes()) }
    val generatedOn = remember { LocalDate.now().format(exportDateFormatter) }
    // 오답 해소율이 실제로 있을 때만 격려 문구를 넣는다(0%인데 "잘 되고 있어요"는 모순).
    val recoveryLine =
        stats.errorRecoveryRate?.takeIf { it > 0f }?.let {
            stringResource(R.string.report_export_recovery, it.toPercentInt())
        }
    return ReportTexts(
        title = stringResource(R.string.report_export_title),
        generatedOn = stringResource(R.string.report_export_generated, generatedOn),
        summary =
            listOf(
                stringResource(R.string.report_total_solved) to stringResource(R.string.home_unit_count, stats.totalSolved),
                stringResource(R.string.report_accuracy) to stringResource(R.string.home_unit_percent, stats.accuracy.toPercentInt()),
                stringResource(R.string.report_current_level) to stringResource(R.string.home_unit_level, stats.currentDifficulty),
                stringResource(R.string.report_streak) to stringResource(R.string.report_unit_days, stats.streakDays),
            ),
        sectionAreaTitle = stringResource(R.string.report_export_section_area),
        sectionWeakTitle = stringResource(R.string.report_export_section_weak),
        sectionMistakeTitle = stringResource(R.string.report_export_section_mistake),
        weakEmpty = stringResource(R.string.report_export_weak_empty),
        mistakeEmpty = stringResource(R.string.report_export_mistake_empty),
        recoveryLine = recoveryLine,
        areaLabels = areaLabels,
        footer = stringResource(R.string.report_export_footer),
    )
}

/** 리포트 PDF를 안드로이드 인쇄 프레임워크로 흘려보낸다(대화상자에서 'PDF로 저장' 선택 가능). */
private fun printReport(
    context: Context,
    stats: LearningStats,
    texts: ReportTexts,
    jobName: String,
) {
    val printManager = context.getSystemService(Context.PRINT_SERVICE) as PrintManager
    val adapter =
        WorksheetPrintAdapter(fileName = "ddakpul-report.pdf") {
            ReportPdfGenerator(stats, texts).generate()
        }
    val attributes =
        PrintAttributes
            .Builder()
            .setMediaSize(PrintAttributes.MediaSize.ISO_A4)
            .build()
    printManager.print(jobName, adapter, attributes)
}

/** 이용권 전용 심화 분석 — 학습량·정답률 추이·성장 곡선·개념 숙달도·난이도별 숙달 지도. */
@Composable
private fun PremiumAnalyticsSections(
    stats: LearningStats,
    dayCells: List<DayCell>,
    masteryGrid: List<MasteryCellUi>,
) {
    Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
        SectionCard(title = stringResource(R.string.report_daily_title), icon = "📊") {
            MiniBarChart(
                entries = dayCells.map { BarEntry(value = it.solved.toFloat(), emphasized = it.isToday) },
                startLabel = dayCells.firstOrNull()?.dateLabel().orEmpty(),
                endLabel = dayCells.lastOrNull()?.dateLabel().orEmpty(),
            )
        }
        SectionCard(title = stringResource(R.string.report_trend_title), icon = "📈") {
            TrendLineChart(
                values = dayCells.map { it.accuracy },
                startLabel = dayCells.firstOrNull()?.dateLabel().orEmpty(),
                endLabel = dayCells.lastOrNull()?.dateLabel().orEmpty(),
            )
        }
        if (stats.difficultyProgress.size >= 2) {
            SectionCard(title = stringResource(R.string.report_growth_title), icon = "🚀") {
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
        if (stats.avgTimeSecByDifficulty.isNotEmpty()) {
            SectionCard(
                title = stringResource(R.string.report_avgtime_title),
                icon = "⏱️",
                subtitle = stringResource(R.string.report_avgtime_caption),
            ) {
                AvgTimeBars(stats.avgTimeSecByDifficulty)
            }
        }
        val concepts = stats.conceptStats.filter { it.solved >= 2 }.take(MAX_CONCEPT_ROWS)
        if (concepts.isNotEmpty()) {
            SectionCard(title = stringResource(R.string.report_concept_title), icon = "🧩") {
                concepts.forEach { concept -> ConceptRow(concept) }
            }
        }
        SectionCard(title = stringResource(R.string.report_matrix_title), icon = "🗺️") {
            MasteryMap(masteryGrid = masteryGrid, currentDifficulty = stats.currentDifficulty)
        }
    }
}

/**
 * '다음 한 걸음' 카드 — 통계를 실행 가능한 코칭 한 줄로(딱풀 핵심 축: 피드백).
 * 민트(앱의 '진행' 강조색) 카드로 눈에 띄게, 필요하면 '지금 풀기'로 바로 이어 준다.
 */
@Composable
private fun NextStepCard(
    nextStep: NextStep,
    onStartSolving: () -> Unit,
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.secondaryContainer),
    ) {
        Column(
            modifier = Modifier.fillMaxWidth().padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            Text(
                text = stringResource(R.string.report_nextstep_label),
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onSecondaryContainer,
            )
            Text(
                text = nextStepText(nextStep),
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.onSecondaryContainer,
            )
            if (nextStep.canSolveNow) {
                Button(onClick = onStartSolving) {
                    Icon(imageVector = Icons.Filled.PlayArrow, contentDescription = null)
                    Text(
                        text = stringResource(R.string.report_nextstep_solve),
                        modifier = Modifier.padding(start = 6.dp),
                    )
                }
            }
        }
    }
}

@Composable
private fun nextStepText(nextStep: NextStep): String =
    when (nextStep) {
        NextStep.StartToday -> {
            stringResource(R.string.report_nextstep_start_today)
        }

        is NextStep.FocusArea -> {
            stringResource(R.string.report_nextstep_focus_area, stringResource(nextStep.area.labelRes()))
        }

        NextStep.ReadyForHarder -> {
            stringResource(R.string.report_nextstep_ready)
        }

        is NextStep.KeepStreak -> {
            stringResource(R.string.report_nextstep_streak, nextStep.days)
        }

        NextStep.Encourage -> {
            stringResource(R.string.report_nextstep_encourage)
        }
    }

/**
 * 히어로 카드 — 이 앱의 성장은 '난이도 등반'이라(학년 개념 없음) 정답률보다 현재 난이도를
 * 앞세운다. 1~7 트랙으로 '어디까지 왔는지'를 한눈에.
 */
@Composable
private fun HeroCard(stats: LearningStats) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer),
    ) {
        Column(
            modifier = Modifier.fillMaxWidth().padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            Text(
                text = stringResource(R.string.report_hero_label),
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onPrimaryContainer,
            )
            Text(
                text = stringResource(R.string.home_unit_level, stats.currentDifficulty),
                style = MaterialTheme.typography.displaySmall,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onPrimaryContainer,
            )
            LevelTrack(current = stats.currentDifficulty, min = Difficulty.MIN, max = Difficulty.MAX)
            Text(
                text = stringResource(R.string.report_hero_caption, Difficulty.MAX),
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.8f),
            )
        }
    }
}

/** 핵심 지표 2×2 — 아이콘·보조 수치(맞음·최고 연속·지난주 대비·오늘)까지 담아 자세하게. */
@Composable
private fun KeyStatTiles(stats: LearningStats) {
    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            StatTile(
                icon = "📚",
                label = stringResource(R.string.report_total_solved),
                value = stringResource(R.string.home_unit_count, stats.totalSolved),
                caption = stringResource(R.string.report_caption_correct, stats.correctCount),
                modifier = Modifier.weight(1f),
            )
            StatTile(
                icon = "🎯",
                label = stringResource(R.string.report_accuracy),
                value = stringResource(R.string.home_unit_percent, stats.accuracy.toPercentInt()),
                caption = accuracyDeltaCaption(stats),
                modifier = Modifier.weight(1f),
            )
        }
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            StatTile(
                icon = "🔥",
                label = stringResource(R.string.report_streak),
                value = stringResource(R.string.report_unit_days, stats.streakDays),
                caption = stringResource(R.string.report_caption_best_streak, stats.bestStreakDays),
                modifier = Modifier.weight(1f),
            )
            StatTile(
                icon = "📅",
                label = stringResource(R.string.report_today),
                value = stringResource(R.string.home_unit_count, stats.todaySolved),
                caption = stringResource(R.string.report_caption_today_time, stats.todayTimeSpentSec / 60),
                modifier = Modifier.weight(1f),
            )
        }
    }
}

/** 최근 7일 vs 그 이전 7일 정답률 차이를 보조 수치로. 둘 다 있어야 계산. */
@Composable
private fun accuracyDeltaCaption(stats: LearningStats): String? {
    val recent = stats.recentAccuracy ?: return null
    val previous = stats.previousAccuracy ?: return null
    val delta = (recent - previous).toPercentInt()
    return when {
        delta > 0 -> stringResource(R.string.report_caption_delta_up, delta)
        delta < 0 -> stringResource(R.string.report_caption_delta_down, -delta)
        else -> stringResource(R.string.report_caption_delta_same)
    }
}

/** 난이도별 평균 풀이 시간 — '어려운 문제에 얼마나 오래 고민하는지'(시간 = 사고의 흔적). */
@Composable
private fun AvgTimeBars(avgByDifficulty: Map<Int, Int>) {
    val maxSec = avgByDifficulty.values.maxOrNull()?.takeIf { it > 0 } ?: return
    val barBg = MaterialTheme.colorScheme.surfaceVariant
    val barFg = MaterialTheme.colorScheme.primary
    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
        for (level in Difficulty.MIN..Difficulty.MAX) {
            val sec = avgByDifficulty[level] ?: continue
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(10.dp),
            ) {
                Text(
                    text = stringResource(R.string.report_avgtime_level, level),
                    style = MaterialTheme.typography.bodyMedium,
                    maxLines = 1,
                    // 큰 글씨 접근성(fontScale↑)에서 "난이도 10"이 60dp를 넘겨 두 줄로 깨지지 않게
                    // 최소폭만 두고 필요하면 늘어나게 한다(고정폭이면 wrap, 여기선 라벨이 온전).
                    modifier = Modifier.widthIn(min = 60.dp),
                )
                ProgressBar(
                    fraction = sec.toFloat() / maxSec,
                    color = barFg,
                    trackColor = barBg,
                    height = 14.dp,
                    modifier = Modifier.weight(1f),
                )
                Text(
                    text = durationText(sec),
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.width(52.dp),
                )
            }
        }
    }
}

@Composable
private fun durationText(sec: Int): String =
    if (sec >= 60) {
        stringResource(R.string.report_avgtime_min, sec / 60)
    } else {
        stringResource(R.string.report_avgtime_sec, sec)
    }

/** 4개 영역을 고정 색으로 구분(밝은 디자인 · 알록달록하되 절제). */
private fun areaColor(area: MathArea) =
    when (area) {
        MathArea.NUMBER_OPERATION -> AreaNumber
        MathArea.CHANGE_RELATION -> AreaChange
        MathArea.SHAPE_MEASUREMENT -> AreaShape
        MathArea.DATA_POSSIBILITY -> AreaData
    }

/** 네 영역별 성취 — 어디가 강하고 어디를 보강할지 한눈에(기본 지표). 시도 없는 영역은 빈 막대로. */
@Composable
private fun AreaBreakdown(areaStats: List<AreaStat>) {
    val byArea = areaStats.associateBy { it.area }
    val barBg = MaterialTheme.colorScheme.surfaceVariant
    Column(verticalArrangement = Arrangement.spacedBy(14.dp)) {
        MathArea.entries.forEach { area ->
            val stat = byArea[area]
            val solved = stat?.solved ?: 0
            val accuracy = stat?.accuracy ?: 0f
            val barFg = areaColor(area)
            Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Text(
                        text = stringResource(area.labelRes()),
                        style = MaterialTheme.typography.bodyLarge,
                        fontWeight = FontWeight.Bold,
                        maxLines = 2,
                        overflow = TextOverflow.Ellipsis,
                        modifier = Modifier.weight(1f),
                    )
                    Text(
                        text =
                            if (solved == 0) {
                                stringResource(R.string.report_area_none)
                            } else {
                                stringResource(R.string.report_area_stat, solved, accuracy.toPercentInt())
                            },
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.padding(start = 8.dp),
                    )
                }
                ProgressBar(
                    fraction = accuracy,
                    color = barFg,
                    trackColor = barBg,
                    modifier = Modifier.fillMaxWidth(),
                )
            }
        }
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
            SectionCard(title = stringResource(R.string.report_weekly_title), icon = "📝") {
                Text(
                    text = summary.toParagraph(),
                    style = MaterialTheme.typography.bodyLarge,
                )
            }
        }

        if (insights.isNotEmpty()) {
            SectionCard(title = stringResource(R.string.report_insights_title), icon = "💡") {
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
private fun MistakeNoteSection(mistakes: List<Problem>) {
    SectionCard(title = stringResource(R.string.report_mistakes_title), icon = "✏️") {
        Text(
            text = stringResource(R.string.report_mistakes_desc),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        mistakes.forEachIndexed { index, problem ->
            if (index > 0) HorizontalDivider()
            MistakeItem(problem)
        }
    }
}

/** 오답 노트 한 문제 — 문제·(그림)·정답·풀이. 도형 문제는 그림이 없으면 뜻이 통하지 않으므로 함께 그린다. */
@Composable
private fun MistakeItem(problem: Problem) {
    val colors = MaterialTheme.colorScheme
    Column(
        modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
        verticalArrangement = Arrangement.spacedBy(6.dp),
    ) {
        Text(text = problem.statement, style = MaterialTheme.typography.bodyMedium)
        problem.figure?.let { ProblemFigureView(figure = it, modifier = Modifier.fillMaxWidth()) }
        Text(
            text = stringResource(R.string.result_correct_answer, problem.choices[problem.answer.correctChoiceIndex]),
            style = MaterialTheme.typography.bodyMedium,
            fontWeight = FontWeight.Bold,
            color = colors.primary,
        )
        problem.explanation?.let {
            Text(text = it, style = MaterialTheme.typography.bodySmall, color = colors.onSurfaceVariant)
        }
    }
}

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
                modifier = Modifier.weight(1f),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                // 개념명이 길면(영어 태그는 30자↑) 통계를 밀어내 글자 단위로 깨지므로,
                // 이름은 남는 폭 안에서 말줄임하고 배지·통계는 항상 온전히 보이게 한다.
                Text(
                    text = concept.concept,
                    style = MaterialTheme.typography.bodyLarge,
                    fontWeight = FontWeight.Bold,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                    modifier = Modifier.weight(1f, fill = false),
                )
                MasteryChip(masteryStageOf(concept.solved, concept.accuracy))
            }
            Text(
                text =
                    stringResource(
                        R.string.report_concept_stat,
                        concept.solved,
                        concept.accuracy.toPercentInt(),
                    ),
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.padding(start = 8.dp),
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
