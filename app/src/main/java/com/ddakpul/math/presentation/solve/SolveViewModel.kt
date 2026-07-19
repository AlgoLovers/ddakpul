package com.ddakpul.math.presentation.solve

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.ddakpul.math.core.common.AppResult
import com.ddakpul.math.domain.model.Attempt
import com.ddakpul.math.domain.model.Cell
import com.ddakpul.math.domain.repository.SolutionVideoRepository
import com.ddakpul.math.domain.usecase.DissectionError
import com.ddakpul.math.domain.usecase.DissectionValidation
import com.ddakpul.math.domain.usecase.ExcludeProblemUseCase
import com.ddakpul.math.domain.usecase.GetNextProblemUseCase
import com.ddakpul.math.domain.usecase.ObserveDailyGoalUseCase
import com.ddakpul.math.domain.usecase.ObserveEntitlementUseCase
import com.ddakpul.math.domain.usecase.ObserveLearningStatsUseCase
import com.ddakpul.math.domain.usecase.SubmitAnswerUseCase
import com.ddakpul.math.domain.usecase.SubmitDissectionUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import java.util.TimeZone
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
        private val submitDissection: SubmitDissectionUseCase,
        private val excludeProblem: ExcludeProblemUseCase,
        private val solutionVideoRepository: SolutionVideoRepository,
        observeStats: ObserveLearningStatsUseCase,
        observeDailyGoal: ObserveDailyGoalUseCase,
        observeEntitlement: ObserveEntitlementUseCase,
    ) : ViewModel() {
        private val _uiState = MutableStateFlow(SolveUiState())
        val uiState: StateFlow<SolveUiState> = _uiState.asStateFlow()

        private var questionStartMillis: Long = 0L

        init {
            loadNext()
            // 오늘 푼 문제 수는 기록이 쌓일 때마다 자동 갱신된다(시도 저장 → Flow 재계산).
            viewModelScope.launch {
                observeStats(
                    zoneOffsetMillis = TimeZone.getDefault().getOffset(System.currentTimeMillis()).toLong(),
                    nowMillis = { System.currentTimeMillis() },
                ).collect { stats ->
                    _uiState.update {
                        it.copy(
                            todaySolved = stats.todaySolved,
                            todayTimeSpentSec = stats.todayTimeSpentSec,
                        )
                    }
                }
            }
            viewModelScope.launch {
                observeDailyGoal().collect { goal ->
                    _uiState.update { it.copy(dailyGoal = goal) }
                }
            }
            viewModelScope.launch {
                observeEntitlement().collect { entitlement ->
                    _uiState.update { it.copy(isPremium = entitlement.hasFullAccess(System.currentTimeMillis())) }
                }
            }
        }

        fun loadNext() {
            _uiState.update { it.copy(phase = SolvePhase.LOADING, selectedIndex = null, result = null) }
            viewModelScope.launch {
                val now = System.currentTimeMillis()
                val result =
                    getNextProblem(
                        todaySolved = _uiState.value.todaySolved,
                        zoneOffsetMillis = TimeZone.getDefault().getOffset(now).toLong(),
                        nowMillis = now,
                    )
                when (result) {
                    is AppResult.Success -> {
                        val recommendation = result.data
                        questionStartMillis = System.currentTimeMillis()
                        val video = solutionVideoRepository.videoForMethod(recommendation.problem.methodCode)
                        _uiState.update { current ->
                            current.copy(
                                phase = SolvePhase.SOLVING,
                                problem = recommendation.problem,
                                area = recommendation.problem.area,
                                // 복습(REVIEW)은 현재 레벨과 다른 난이도일 수 있으니 문제 자체의 난이도를 보여준다.
                                difficulty = recommendation.problem.difficulty,
                                selectedIndex = null,
                                result = null,
                                showExplanation = recommendation.showExplanation,
                                reason = recommendation.reason,
                                premiumSuggested = recommendation.premiumSuggested,
                                solutionVideo = video,
                                dissectionAssignment = emptyMap(),
                                dissectionPiece = 0,
                                dissectionResult = null,
                            )
                        }
                    }

                    is AppResult.Failure -> {
                        _uiState.update { it.copy(phase = SolvePhase.EMPTY) }
                    }
                }
            }
        }

        /**
         * 지금 화면의 문제를 "별로예요"로 제외하고 다음 문제로 넘어간다.
         * 풀이 중이든 채점 후든 동작은 같다 — 제외한 문제는 다시 나오지 않는다.
         */
        fun excludeCurrent() {
            val problem = _uiState.value.problem ?: return
            viewModelScope.launch {
                excludeProblem(
                    problemId = problem.id,
                    timestampMillis = System.currentTimeMillis(),
                )
                loadNext()
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
                // 상한 필수: 문제를 열어둔 채 기기가 잠들면(저녁·밤새) 경과 시간이 통째로 기록돼
                // 평균 통계를 영구히 왜곡한다. 사고력 문제 기준 30분이면 충분히 관대한 상한.
                val elapsedSec =
                    ((System.currentTimeMillis() - questionStartMillis) / MILLIS_PER_SECOND)
                        .toInt()
                        .coerceIn(0, Attempt.MAX_TIME_SPENT_SEC)
                val gradingResult =
                    submitAnswer(
                        problem = problem,
                        selectedIndex = selected,
                        timeSpentSec = elapsedSec,
                        timestamp = System.currentTimeMillis(),
                    )
                _uiState.update {
                    it.copy(
                        phase = SolvePhase.GRADED,
                        result = gradingResult,
                        sessionStreak = if (gradingResult.isCorrect) it.sessionStreak + 1 else 0,
                    )
                }
            }
        }

        // ── 등분 퍼즐(구성형) 조작·채점 ──
        fun selectDissectionPiece(pieceId: Int) {
            if (_uiState.value.phase != SolvePhase.SOLVING) return
            _uiState.update { it.copy(dissectionPiece = pieceId) }
        }

        /** 칸을 탭 — 선택한 조각으로 칠하고, 같은 조각을 다시 탭하면 지운다(토글). */
        fun tapDissectionCell(cell: Cell) {
            if (_uiState.value.phase != SolvePhase.SOLVING) return
            _uiState.update { s ->
                val next =
                    if (s.dissectionAssignment[cell] == s.dissectionPiece) {
                        s.dissectionAssignment - cell
                    } else {
                        s.dissectionAssignment + (cell to s.dissectionPiece)
                    }
                s.copy(dissectionAssignment = next)
            }
        }

        fun clearDissection() {
            if (_uiState.value.phase != SolvePhase.SOLVING) return
            _uiState.update { it.copy(dissectionAssignment = emptyMap()) }
        }

        fun submitDissection() {
            val current = _uiState.value
            val puzzle = current.problem?.dissection ?: return
            if (current.phase != SolvePhase.SOLVING) return
            // 미완성(칸을 다 안 채움)은 실제 답이 아니므로 시도 기록 없이 힌트만 — 계속 풀 수 있게 SOLVING 유지.
            if (current.dissectionAssignment.keys != puzzle.cells.toSet()) {
                _uiState.update { it.copy(dissectionResult = DissectionValidation(false, DissectionError.INCOMPLETE)) }
                return
            }
            val problem = current.problem
            viewModelScope.launch {
                val elapsedSec =
                    ((System.currentTimeMillis() - questionStartMillis) / MILLIS_PER_SECOND)
                        .toInt()
                        .coerceIn(0, Attempt.MAX_TIME_SPENT_SEC)
                val validation =
                    submitDissection(
                        problem = problem,
                        assignment = current.dissectionAssignment,
                        timeSpentSec = elapsedSec,
                        timestamp = System.currentTimeMillis(),
                    )
                _uiState.update {
                    it.copy(
                        phase = SolvePhase.GRADED,
                        dissectionResult = validation,
                        sessionStreak = if (validation.isValid) it.sessionStreak + 1 else 0,
                    )
                }
            }
        }

        private companion object {
            const val MILLIS_PER_SECOND = 1000L
        }
    }
