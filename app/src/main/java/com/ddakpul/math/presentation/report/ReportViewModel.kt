package com.ddakpul.math.presentation.report

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.ddakpul.math.domain.model.Difficulty
import com.ddakpul.math.domain.model.LearningStats
import com.ddakpul.math.domain.model.MathArea
import com.ddakpul.math.domain.model.SessionGoals
import com.ddakpul.math.domain.usecase.ObserveLearningStatsUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.stateIn
import java.util.TimeZone
import javax.inject.Inject
import kotlin.math.roundToInt

/** 최근 N일 창의 하루 칸. 학습이 없던 날은 solved=0, accuracy=null. */
data class DayCell(
    val epochDay: Long,
    val solved: Int,
    val accuracy: Float?,
    val isToday: Boolean,
)

/**
 * 숙달 지도의 한 칸(영역×난이도). [stats.matrixCells]는 시도가 있는 칸만 담으므로,
 * 시도 없는 칸도 solved=0으로 채워 4×5 그리드를 항상 완성한다.
 */
data class MasteryCellUi(
    val area: MathArea,
    val difficulty: Int,
    val solved: Int,
    val accuracy: Float?,
)

/**
 * 학부모에게 보여줄 문장형 인사이트 — 데이터 해석을 끝낸 "말"이 차트보다 잘 읽힌다.
 * 문구 매핑은 화면(리소스)에서 한다.
 */
sealed interface ReportInsight {
    data class Streak(
        val days: Int,
    ) : ReportInsight

    data class AccuracyUp(
        val deltaPercentPoint: Int,
    ) : ReportInsight

    data class AccuracyDown(
        val deltaPercentPoint: Int,
    ) : ReportInsight

    data class ErrorRecovery(
        val percent: Int,
    ) : ReportInsight

    data class WeakConcept(
        val concept: String,
        val percent: Int,
    ) : ReportInsight

    data object GoalDone : ReportInsight
}

/** 이번 주(최근 7일) 요약 — 학부모 소통의 최선 관행인 "주간 요약 문단"의 재료. */
data class WeeklySummary(
    val solved: Int,
    val studyDays: Int,
    val accuracyPercent: Int,
    /** 지난주 대비 정답률 변화(%p). 비교 불가면 null. */
    val deltaPercentPoint: Int?,
    /** 보강 권장 개념. 없으면 null. */
    val weakConcept: String?,
)

data class ReportUiState(
    val stats: LearningStats? = null,
    val isLoading: Boolean = true,
    val dayCells: List<DayCell> = emptyList(),
    val insights: List<ReportInsight> = emptyList(),
    val weeklySummary: WeeklySummary? = null,
    val masteryGrid: List<MasteryCellUi> = emptyList(),
)

@HiltViewModel
class ReportViewModel
    @Inject
    constructor(
        observeStats: ObserveLearningStatsUseCase,
    ) : ViewModel() {
        val uiState: StateFlow<ReportUiState> =
            observeStats(
                zoneOffsetMillis = zoneOffsetMillis(),
                nowMillis = { System.currentTimeMillis() },
            ).map { stats ->
                ReportUiState(
                    stats = stats,
                    isLoading = false,
                    dayCells = buildDayCells(stats),
                    insights = buildInsights(stats),
                    weeklySummary = buildWeeklySummary(stats),
                    masteryGrid = buildMasteryGrid(stats),
                )
            }.stateIn(
                scope = viewModelScope,
                started = SharingStarted.WhileSubscribed(STOP_TIMEOUT_MILLIS),
                initialValue = ReportUiState(),
            )

        /** 최근 [WINDOW_DAYS]일을 빈 날 포함해 채운다 — 차트의 x축이 끊기지 않게. */
        private fun buildDayCells(stats: LearningStats): List<DayCell> {
            val today =
                Math.floorDiv(System.currentTimeMillis() + zoneOffsetMillis(), MILLIS_PER_DAY)
            val byDay = stats.dailyStats.associateBy { it.epochDay }
            return ((today - WINDOW_DAYS + 1)..today).map { day ->
                val stat = byDay[day]
                DayCell(
                    epochDay = day,
                    solved = stat?.solved ?: 0,
                    accuracy = stat?.let { if (it.solved > 0) it.accuracy else null },
                    isToday = day == today,
                )
            }
        }

        /**
         * 영역×난이도 20칸을 전부 채운다 — 시도 없는 칸도 solved=0으로 그리드에 나타나야 한다.
         * [stats.matrixCells]는 시도가 있는 칸만 담으므로(집계 로직상 solved=0인 칸은 만들어지지
         * 않는다) `cell`이 있으면 항상 solved > 0이다.
         */
        private fun buildMasteryGrid(stats: LearningStats): List<MasteryCellUi> {
            val byKey = stats.matrixCells.associateBy { it.area to it.difficulty }
            return MathArea.entries.flatMap { area ->
                (Difficulty.MIN..Difficulty.MAX).map { difficulty ->
                    val cell = byKey[area to difficulty]
                    MasteryCellUi(
                        area = area,
                        difficulty = difficulty,
                        solved = cell?.solved ?: 0,
                        accuracy = cell?.accuracy,
                    )
                }
            }
        }

        private fun buildInsights(stats: LearningStats): List<ReportInsight> =
            buildList {
                if (stats.todaySolved >= SessionGoals.DAILY_GOAL_PROBLEMS) add(ReportInsight.GoalDone)
                if (stats.streakDays >= MIN_STREAK_FOR_INSIGHT) add(ReportInsight.Streak(stats.streakDays))

                val recent = stats.recentAccuracy
                val previous = stats.previousAccuracy
                if (recent != null && previous != null) {
                    val delta = ((recent - previous) * 100).roundToInt()
                    when {
                        delta >= TREND_DELTA_THRESHOLD -> add(ReportInsight.AccuracyUp(delta))
                        delta <= -TREND_DELTA_THRESHOLD -> add(ReportInsight.AccuracyDown(-delta))
                    }
                }

                stats.errorRecoveryRate
                    ?.takeIf { it > 0f }
                    ?.let { add(ReportInsight.ErrorRecovery((it * 100).roundToInt())) }

                stats.conceptStats
                    .firstOrNull { it.solved >= MIN_SOLVED_FOR_CONCEPT && it.accuracy < WEAK_ACCURACY }
                    ?.let { add(ReportInsight.WeakConcept(it.concept, (it.accuracy * 100).roundToInt())) }
            }

        private fun buildWeeklySummary(stats: LearningStats): WeeklySummary {
            val today =
                Math.floorDiv(System.currentTimeMillis() + zoneOffsetMillis(), MILLIS_PER_DAY)
            val lastWeek = stats.dailyStats.filter { it.epochDay > today - DAYS_PER_WEEK }
            val solved = lastWeek.sumOf { it.solved }
            val correct = lastWeek.sumOf { it.correct }

            val recent = stats.recentAccuracy
            val previous = stats.previousAccuracy
            val delta =
                if (recent != null && previous != null) ((recent - previous) * 100).roundToInt() else null

            return WeeklySummary(
                solved = solved,
                studyDays = lastWeek.count { it.solved > 0 },
                accuracyPercent = if (solved > 0) correct * 100 / solved else 0,
                deltaPercentPoint = delta,
                weakConcept =
                    stats.conceptStats
                        .firstOrNull { it.solved >= MIN_SOLVED_FOR_CONCEPT && it.accuracy < WEAK_ACCURACY }
                        ?.concept,
            )
        }

        private fun zoneOffsetMillis(): Long = TimeZone.getDefault().getOffset(System.currentTimeMillis()).toLong()

        private companion object {
            const val STOP_TIMEOUT_MILLIS = 5_000L
            const val MILLIS_PER_DAY = 86_400_000L
            const val WINDOW_DAYS = 14L
            const val DAYS_PER_WEEK = 7L

            /** 인사이트로 띄울 최소 연속 학습일. */
            const val MIN_STREAK_FOR_INSIGHT = 2

            /** 정답률 추이 인사이트를 띄우는 최소 변화폭(%p). */
            const val TREND_DELTA_THRESHOLD = 5

            /** 개념 인사이트를 띄우려면 최소 이만큼은 풀어봤어야 한다. */
            const val MIN_SOLVED_FOR_CONCEPT = 3

            /** 이 정답률 미만이면 "보강 필요" 개념. */
            const val WEAK_ACCURACY = 0.6f
        }
    }
