package com.ddakpul.math.presentation.report

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.ddakpul.math.domain.common.MILLIS_PER_DAY
import com.ddakpul.math.domain.model.LearningReport
import com.ddakpul.math.domain.model.LearningStats
import com.ddakpul.math.domain.model.NextStep
import com.ddakpul.math.domain.time.Clock
import com.ddakpul.math.domain.usecase.BuildLearningReportUseCase
import com.ddakpul.math.domain.usecase.ComputeNextStepUseCase
import com.ddakpul.math.domain.usecase.ObserveDailyGoalUseCase
import com.ddakpul.math.domain.usecase.ObserveLearningStatsUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.stateIn
import javax.inject.Inject

data class ReportUiState(
    val stats: LearningStats? = null,
    val isLoading: Boolean = true,
    /** 통계를 학부모용 해석(인사이트·주간 요약·숙달 지도)으로 옮긴 결과. */
    val report: LearningReport = LearningReport.EMPTY,
    /** '다음 한 걸음' — 통계를 실행 가능한 코칭으로. */
    val nextStep: NextStep? = null,
)

/**
 * 리포트 화면의 상태. 해석은 전부 domain([BuildLearningReportUseCase])이 하고,
 * 여기서는 스트림을 합쳐 화면 상태로 옮기기만 한다.
 */
@HiltViewModel
class ReportViewModel
    @Inject
    constructor(
        observeStats: ObserveLearningStatsUseCase,
        observeDailyGoal: ObserveDailyGoalUseCase,
        private val computeNextStep: ComputeNextStepUseCase,
        private val buildReport: BuildLearningReportUseCase,
        private val clock: Clock,
    ) : ViewModel() {
        val uiState: StateFlow<ReportUiState> =
            combine(
                observeStats(
                    zoneOffsetMillis = clock.zoneOffsetMillis(),
                    nowMillis = clock::nowMillis,
                ),
                observeDailyGoal(),
            ) { stats, dailyGoal ->
                ReportUiState(
                    stats = stats,
                    isLoading = false,
                    report = buildReport(stats = stats, dailyGoal = dailyGoal, today = today()),
                    nextStep = computeNextStep(stats),
                )
            }.stateIn(
                scope = viewModelScope,
                started = SharingStarted.WhileSubscribed(STOP_TIMEOUT_MILLIS),
                initialValue = ReportUiState(),
            )

        /** 로컬 자정 기준 오늘의 epoch day. */
        private fun today(): Long = Math.floorDiv(clock.nowMillis() + clock.zoneOffsetMillis(), MILLIS_PER_DAY)

        private companion object {
            const val STOP_TIMEOUT_MILLIS = 5_000L
        }
    }
