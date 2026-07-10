package com.ddakpul.math.presentation.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.ddakpul.math.domain.model.LearnerReport
import com.ddakpul.math.domain.usecase.ObserveLearnerReportUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.stateIn
import javax.inject.Inject

data class HomeUiState(
    val report: LearnerReport? = null,
)

@HiltViewModel
class HomeViewModel
    @Inject
    constructor(
        observeReport: ObserveLearnerReportUseCase,
    ) : ViewModel() {
        val uiState: StateFlow<HomeUiState> =
            observeReport()
                .map { HomeUiState(report = it) }
                .stateIn(
                    scope = viewModelScope,
                    started = SharingStarted.WhileSubscribed(STOP_TIMEOUT_MILLIS),
                    initialValue = HomeUiState(),
                )

        private companion object {
            const val STOP_TIMEOUT_MILLIS = 5_000L
        }
    }
