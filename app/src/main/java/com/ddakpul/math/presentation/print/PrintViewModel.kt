package com.ddakpul.math.presentation.print

import androidx.lifecycle.ViewModel
import com.ddakpul.math.domain.model.MathArea
import com.ddakpul.math.domain.model.Problem
import com.ddakpul.math.domain.usecase.BuildWorksheetUseCase
import com.ddakpul.math.domain.usecase.WorksheetSource
import com.ddakpul.math.domain.usecase.WorksheetSpec
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import javax.inject.Inject

/** 인쇄 옵션. 문항 수 선택지는 A4 학습지 권장 분량(리서치: 문장제 4~6문항/장) 기준. */
data class PrintUiState(
    val count: Int = DEFAULT_COUNT,
    val source: WorksheetSource = WorksheetSource.RECOMMENDED,
    val area: MathArea? = null,
    val includeAnswers: Boolean = true,
) {
    companion object {
        const val DEFAULT_COUNT = 10
        val COUNT_OPTIONS = listOf(5, 10, 15)
    }
}

@HiltViewModel
class PrintViewModel
    @Inject
    constructor(
        private val buildWorksheet: BuildWorksheetUseCase,
    ) : ViewModel() {
        private val _uiState = MutableStateFlow(PrintUiState())
        val uiState: StateFlow<PrintUiState> = _uiState.asStateFlow()

        fun setCount(count: Int) = _uiState.update { it.copy(count = count) }

        fun setSource(source: WorksheetSource) = _uiState.update { it.copy(source = source) }

        fun setArea(area: MathArea?) = _uiState.update { it.copy(area = area) }

        fun toggleIncludeAnswers() = _uiState.update { it.copy(includeAnswers = !it.includeAnswers) }

        /** 현재 옵션으로 학습지 문제를 뽑는다. 인쇄물은 쉬움→어려움 순으로 배치한다. */
        suspend fun buildProblems(): List<Problem> {
            val state = _uiState.value
            return buildWorksheet(WorksheetSpec(count = state.count, source = state.source, area = state.area))
                .sortedBy { it.difficulty }
        }
    }
