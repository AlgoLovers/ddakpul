package com.ddakpul.math.presentation.solve

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.ddakpul.math.core.common.AppResult
import com.ddakpul.math.domain.usecase.GetNextProblemUseCase
import com.ddakpul.math.domain.usecase.SubmitAnswerUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * 문제 풀이의 한 바퀴(추천 → 풀이 → 채점 → 다음)를 관장한다.
 * ViewModel은 UseCase만 호출하고, 시간(now)은 여기서 주입해 domain을 순수하게 유지한다.
 */
@HiltViewModel
class SolveViewModel
    @Inject
    constructor(
        private val getNextProblem: GetNextProblemUseCase,
        private val submitAnswer: SubmitAnswerUseCase,
    ) : ViewModel() {
        private val _uiState = MutableStateFlow(SolveUiState())
        val uiState: StateFlow<SolveUiState> = _uiState.asStateFlow()

        private var questionStartMillis: Long = 0L

        init {
            loadNext()
        }

        fun loadNext() {
            _uiState.update { it.copy(phase = SolvePhase.LOADING, selectedIndex = null, result = null) }
            viewModelScope.launch {
                when (val result = getNextProblem()) {
                    is AppResult.Success -> {
                        val recommendation = result.data
                        questionStartMillis = System.currentTimeMillis()
                        _uiState.update {
                            SolveUiState(
                                phase = SolvePhase.SOLVING,
                                problem = recommendation.problem,
                                area = recommendation.problem.area,
                                difficulty = recommendation.targetDifficulty,
                                showExplanation = recommendation.showExplanation,
                                reason = recommendation.reason,
                            )
                        }
                    }

                    is AppResult.Failure -> {
                        _uiState.update { it.copy(phase = SolvePhase.EMPTY) }
                    }
                }
            }
        }

        fun selectChoice(index: Int) {
            if (_uiState.value.phase != SolvePhase.SOLVING) return
            _uiState.update { it.copy(selectedIndex = index) }
        }

        fun submit() {
            val current = _uiState.value
            val problem = current.problem ?: return
            val selected = current.selectedIndex ?: return
            if (current.phase != SolvePhase.SOLVING) return

            viewModelScope.launch {
                val elapsedSec =
                    ((System.currentTimeMillis() - questionStartMillis) / MILLIS_PER_SECOND)
                        .toInt()
                        .coerceAtLeast(0)
                val gradingResult =
                    submitAnswer(
                        problem = problem,
                        selectedIndex = selected,
                        timeSpentSec = elapsedSec,
                        timestamp = System.currentTimeMillis(),
                    )
                _uiState.update { it.copy(phase = SolvePhase.GRADED, result = gradingResult) }
            }
        }

        private companion object {
            const val MILLIS_PER_SECOND = 1000L
        }
    }
