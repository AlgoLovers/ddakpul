package com.ddakpul.math.presentation.settings

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.ddakpul.math.domain.model.SessionGoals
import com.ddakpul.math.domain.usecase.ObserveDailyGoalUseCase
import com.ddakpul.math.domain.usecase.ResetProgressUseCase
import com.ddakpul.math.domain.usecase.SetDailyGoalUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import javax.inject.Inject

data class SettingsUiState(
    val dailyGoal: Int = SessionGoals.DAILY_GOAL_PROBLEMS,
)

@HiltViewModel
class SettingsViewModel
    @Inject
    constructor(
        observeDailyGoal: ObserveDailyGoalUseCase,
        private val setDailyGoal: SetDailyGoalUseCase,
        private val resetProgress: ResetProgressUseCase,
    ) : ViewModel() {
        val uiState: StateFlow<SettingsUiState> =
            observeDailyGoal()
                .map { SettingsUiState(dailyGoal = it) }
                .stateIn(
                    scope = viewModelScope,
                    started = SharingStarted.WhileSubscribed(STOP_TIMEOUT_MILLIS),
                    initialValue = SettingsUiState(),
                )

        fun setDailyGoal(goal: Int) {
            viewModelScope.launch { setDailyGoal.invoke(goal) }
        }

        fun resetProgress() {
            viewModelScope.launch { resetProgress.invoke() }
        }

        private companion object {
            const val STOP_TIMEOUT_MILLIS = 5_000L
        }
    }
