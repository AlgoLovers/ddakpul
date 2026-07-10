package com.ddakpul.math.presentation.home

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

data class HomeUiState(
    val stats: LearningStats? = null,
)

@HiltViewModel
class HomeViewModel
    @Inject
    constructor(
        observeStats: ObserveLearningStatsUseCase,
    ) : ViewModel() {
        val uiState: StateFlow<HomeUiState> =
            observeStats(
                zoneOffsetMillis = TimeZone.getDefault().getOffset(System.currentTimeMillis()).toLong(),
                nowMillis = { System.currentTimeMillis() },
            ).map { HomeUiState(stats = it) }
                .stateIn(
                    scope = viewModelScope,
                    started = SharingStarted.WhileSubscribed(STOP_TIMEOUT_MILLIS),
                    initialValue = HomeUiState(),
                )

        private companion object {
            const val STOP_TIMEOUT_MILLIS = 5_000L
        }
    }
