package com.ddakpul.math.presentation.report

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

data class ReportUiState(
    val report: LearnerReport? = null,
    val isLoading: Boolean = true,
)

@HiltViewModel
class ReportViewModel
    @Inject
    constructor(
        observeReport: ObserveLearnerReportUseCase,
    ) : ViewModel() {
        val uiState: StateFlow<ReportUiState> =
            observeReport()
                .map { ReportUiState(report = it, isLoading = false) }
                .stateIn(
                    scope = viewModelScope,
                    started = SharingStarted.WhileSubscribed(STOP_TIMEOUT_MILLIS),
                    initialValue = ReportUiState(),
                )

        private companion object {
            const val STOP_TIMEOUT_MILLIS = 5_000L
        }
    }
