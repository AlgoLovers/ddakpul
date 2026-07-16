package com.ddakpul.math.presentation.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.ddakpul.math.domain.model.LearningStats
import com.ddakpul.math.domain.model.Monetization
import com.ddakpul.math.domain.model.SessionGoals
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
    /** 출시 기념 무료 마감 시각. 0이면 프로모션 아님(배너 숨김). */
    val launchFreeUntilMillis: Long = 0L,
)

@HiltViewModel
class HomeViewModel
    @Inject
    constructor(
        observeStats: ObserveLearningStatsUseCase,
        observeDailyGoal: ObserveDailyGoalUseCase,
    ) : ViewModel() {
        val uiState: StateFlow<HomeUiState> =
            combine(
                observeStats(
                    zoneOffsetMillis = TimeZone.getDefault().getOffset(System.currentTimeMillis()).toLong(),
                    nowMillis = { System.currentTimeMillis() },
                ),
                observeDailyGoal(),
            ) { stats, goal ->
                HomeUiState(
                    stats = stats,
                    dailyGoal = goal,
                    launchFreeUntilMillis =
                        Monetization.LAUNCH_FREE_UNTIL_MILLIS
                            .takeIf { Monetization.isLaunchFree(System.currentTimeMillis()) } ?: 0L,
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
