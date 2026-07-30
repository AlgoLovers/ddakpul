package com.ddakpul.math.presentation.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.ddakpul.math.domain.model.LearningStats
import com.ddakpul.math.domain.model.SessionGoals
import com.ddakpul.math.domain.usecase.CountDueReviewsUseCase
import com.ddakpul.math.domain.usecase.ObserveDailyGoalUseCase
import com.ddakpul.math.domain.usecase.ObserveLearningStatsUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.stateIn
import java.util.TimeZone
import javax.inject.Inject

data class HomeUiState(
    val stats: LearningStats? = null,
    val dailyGoal: Int = SessionGoals.DAILY_GOAL_PROBLEMS,
    /** 오늘 복습이 만기된 그룹 수 — 0이면 복습 카드를 숨긴다. */
    val reviewDueCount: Int = 0,
)

@HiltViewModel
class HomeViewModel
    @Inject
    constructor(
        observeStats: ObserveLearningStatsUseCase,
        observeDailyGoal: ObserveDailyGoalUseCase,
        countDueReviews: CountDueReviewsUseCase,
    ) : ViewModel() {
        val uiState: StateFlow<HomeUiState> =
            combine(
                observeStats(
                    zoneOffsetMillis = TimeZone.getDefault().getOffset(System.currentTimeMillis()).toLong(),
                    nowMillis = { System.currentTimeMillis() },
                ),
                observeDailyGoal(),
            ) { stats, goal ->
                // 시도 기록이 바뀔 때마다 stats가 다시 흐르므로, 복습 만기 수도 같은 타이밍에 재계산된다.
                val now = System.currentTimeMillis()
                HomeUiState(
                    stats = stats,
                    dailyGoal = goal,
                    reviewDueCount =
                        countDueReviews(
                            zoneOffsetMillis = TimeZone.getDefault().getOffset(now).toLong(),
                            nowMillis = now,
                        ),
                )
            }.stateIn(
                scope = viewModelScope,
                started = SharingStarted.WhileSubscribed(STOP_TIMEOUT_MILLIS),
                initialValue = HomeUiState(),
            )

        private companion object {
            const val STOP_TIMEOUT_MILLIS = 5_000L
        }
    }
