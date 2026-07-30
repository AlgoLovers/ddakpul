package com.ddakpul.math.presentation.review

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.ddakpul.math.domain.model.WrongProblem
import com.ddakpul.math.domain.usecase.ObserveWrongProblemsUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.stateIn
import javax.inject.Inject

/** 오답 노트 화면 상태 — 마지막으로 틀린 순으로 정렬된 오답 문제 목록. */
data class ReviewUiState(
    val wrongProblems: List<WrongProblem> = emptyList(),
    val isLoading: Boolean = true,
)

/** 오답 노트 화면의 ViewModel. 시도가 바뀌면(복습 재풀이로 정답이 되면) 목록이 자동 갱신된다. */
@HiltViewModel
class ReviewViewModel
    @Inject
    constructor(
        observeWrongProblems: ObserveWrongProblemsUseCase,
    ) : ViewModel() {
        val uiState: StateFlow<ReviewUiState> =
            observeWrongProblems()
                .map { ReviewUiState(wrongProblems = it, isLoading = false) }
                .stateIn(
                    scope = viewModelScope,
                    started = SharingStarted.WhileSubscribed(STOP_TIMEOUT_MILLIS),
                    initialValue = ReviewUiState(),
                )

        private companion object {
            const val STOP_TIMEOUT_MILLIS = 5_000L
        }
    }
