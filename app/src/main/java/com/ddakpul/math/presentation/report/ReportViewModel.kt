package com.ddakpul.math.presentation.report

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.ddakpul.math.domain.model.LearningStats
import com.ddakpul.math.domain.usecase.ObserveLearningStatsUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.stateIn
import java.util.TimeZone
import javax.inject.Inject

data class ReportUiState(
    val stats: LearningStats? = null,
    val isLoading: Boolean = true,
)

@HiltViewModel
class ReportViewModel
    @Inject
    constructor(
        observeStats: ObserveLearningStatsUseCase,
    ) : ViewModel() {
        val uiState: StateFlow<ReportUiState> =
            observeStats(
                zoneOffsetMillis = TimeZone.getDefault().getOffset(System.currentTimeMillis()).toLong(),
                nowMillis = { System.currentTimeMillis() },
            ).map { ReportUiState(stats = it, isLoading = false) }
                .stateIn(
                    scope = viewModelScope,
                    started = SharingStarted.WhileSubscribed(STOP_TIMEOUT_MILLIS),
                    initialValue = ReportUiState(),
                )

        private companion object {
            const val STOP_TIMEOUT_MILLIS = 5_000L
        }
    }
