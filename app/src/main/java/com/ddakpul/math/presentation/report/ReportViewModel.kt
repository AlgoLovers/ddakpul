package com.ddakpul.math.presentation.report

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.ddakpul.math.domain.model.LearningStats
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

data class ReportUiState(
    val stats: LearningStats? = null,
    val isLoading: Boolean = true,
    val dayCells: List<DayCell> = emptyList(),
    val insights: List<ReportInsight> = emptyList(),
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

        private fun zoneOffsetMillis(): Long = TimeZone.getDefault().getOffset(System.currentTimeMillis()).toLong()

        private companion object {
            const val STOP_TIMEOUT_MILLIS = 5_000L
            const val MILLIS_PER_DAY = 86_400_000L
            const val WINDOW_DAYS = 14L

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
