package com.ddakpul.math.presentation.solve

import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.ddakpul.math.domain.common.AppResult
import com.ddakpul.math.domain.model.Attempt
import com.ddakpul.math.domain.model.Cell
import com.ddakpul.math.domain.model.RecommendationReason
import com.ddakpul.math.domain.time.Clock
import com.ddakpul.math.domain.usecase.DissectionError
import com.ddakpul.math.domain.usecase.DissectionValidation
import com.ddakpul.math.domain.usecase.ExcludeProblemUseCase
import com.ddakpul.math.domain.usecase.GetNextProblemUseCase
import com.ddakpul.math.domain.usecase.GetProblemByIdUseCase
import com.ddakpul.math.domain.usecase.GetSolutionVideoUseCase
import com.ddakpul.math.domain.usecase.ObserveDailyGoalUseCase
import com.ddakpul.math.domain.usecase.ObserveLearningStatsUseCase
import com.ddakpul.math.domain.usecase.SubmitAnswerUseCase
import com.ddakpul.math.domain.usecase.SubmitDissectionUseCase
import com.ddakpul.math.domain.usecase.SubmitGiveUpUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
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
        private val getProblemById: GetProblemByIdUseCase,
        private val submitAnswer: SubmitAnswerUseCase,
        private val submitDissection: SubmitDissectionUseCase,
        private val submitGiveUp: SubmitGiveUpUseCase,
        private val excludeProblem: ExcludeProblemUseCase,
        private val getSolutionVideo: GetSolutionVideoUseCase,
        observeStats: ObserveLearningStatsUseCase,
        observeDailyGoal: ObserveDailyGoalUseCase,
        private val clock: Clock,
        savedStateHandle: SavedStateHandle,
    ) : ViewModel() {
        private val _uiState = MutableStateFlow(SolveUiState())
        val uiState: StateFlow<SolveUiState> = _uiState.asStateFlow()

        private var questionStartMillis: Long = 0L

        /** 이번 화면 세션이 시작된 시각 — 소프트 컷은 '오늘 누적'이 아니라 이 세션 경과로 판단한다. */
        private val sessionStartMillis: Long = clock.nowMillis()

        /** 오늘 푼 수를 한 번이라도 읽었는지 — 첫 추천이 0을 보고 도는 것을 막는 신호. */
        private val statsLoaded = MutableStateFlow(false)

        /**
         * 채점 진행 중 플래그. 가드(phase 검사)와 상태 전환 사이에 suspend 구간이 있어,
         * 연타하면 같은 문제가 두 번 기록되고 통계·난이도 스트릭이 오염된다(되돌릴 수 없다).
         * 아이가 쓰는 앱이라 연타는 상수로 봐야 한다.
         *
         * **반드시 채점 코루틴의 `finally`에서 내린다** — 내리지 않으면 첫 제출 이후 이 화면의
         * 모든 제출이 영구히 막힌다(같은 ViewModel이 다음 문제까지 재사용되므로).
         */
        private var submitting = false

        /** 진행 중인 문제 로드 — 연타 시 이전 요청을 취소해 결과가 뒤섞이지 않게 한다. */
        private var loadJob: Job? = null

        /** 오답 노트에서 넘어온 복습 대상 문제 id(있으면 이 문제 하나만 다시 푼다). */
        private val reviewProblemId: String? = savedStateHandle[ARG_REVIEW_PROBLEM_ID]

        init {
            // 오늘 푼 수를 먼저 채운 뒤 첫 문제를 뽑는다 — 순서가 반대면 todaySolved=0으로
            // 추천이 돌아 복습 슬롯(규칙8: todaySolved % 3 == 2)이 진입 직후엔 절대 안 걸린다(2026-08 QA).
            viewModelScope.launch {
                if (reviewProblemId != null) {
                    loadReview(reviewProblemId)
                } else {
                    statsLoaded.first { it }
                    loadNext()
                }
            }
            // 오늘 푼 문제 수는 기록이 쌓일 때마다 자동 갱신된다(시도 저장 → Flow 재계산).
            viewModelScope.launch {
                observeStats(
                    zoneOffsetMillis = clock.zoneOffsetMillis(),
                    nowMillis = clock::nowMillis,
                ).collect { stats ->
                    _uiState.update {
                        it.copy(
                            todaySolved = stats.todaySolved,
                            todayTimeSpentSec = stats.todayTimeSpentSec,
                        )
                    }
                    statsLoaded.value = true
                }
            }
            viewModelScope.launch {
                observeDailyGoal().collect { goal ->
                    _uiState.update { it.copy(dailyGoal = goal) }
                }
            }
        }

        fun loadNext() {
            loadJob?.cancel()
            _uiState.update { it.copy(phase = SolvePhase.LOADING, selectedIndex = null, result = null) }
            loadJob =
                viewModelScope.launch {
                    val now = clock.nowMillis()
                    val result =
                        getNextProblem(
                            todaySolved = _uiState.value.todaySolved,
                            zoneOffsetMillis = clock.zoneOffsetMillis(),
                            nowMillis = now,
                        )
                    when (result) {
                        is AppResult.Success -> {
                            val recommendation = result.data
                            questionStartMillis = clock.nowMillis()
                            _uiState.update { current ->
                                current.copy(
                                    phase = SolvePhase.SOLVING,
                                    problemOrdinal = current.todaySolved + 1,
                                    problem = recommendation.problem,
                                    area = recommendation.problem.area,
                                    // 복습(REVIEW)은 현재 레벨과 다른 난이도일 수 있으니 문제 자체의 난이도를 보여준다.
                                    difficulty = recommendation.problem.difficulty,
                                    selectedIndex = null,
                                    result = null,
                                    showExplanation = recommendation.showExplanation,
                                    reason = recommendation.reason,
                                    solutionVideo = null,
                                    dissectionAssignment = emptyMap(),
                                    dissectionPiece = 0,
                                    dissectionResult = null,
                                )
                            }
                            fillSolutionVideo(recommendation.problem.id, recommendation.problem.methodCode)
                        }

                        is AppResult.Failure -> {
                            _uiState.update { it.copy(phase = SolvePhase.EMPTY) }
                        }
                    }
                }
        }

        /**
         * 해설 영상 유무를 문제 표시 뒤에 따로 채운다 — 매니페스트 조회가 네트워크를 타는데
         * 문제 로드 경로에 두면 연결이 나쁠 때 '다음 문제'가 최대 45초 스피너가 된다.
         */
        private fun fillSolutionVideo(
            problemId: String,
            methodCode: String?,
        ) {
            viewModelScope.launch {
                val video = getSolutionVideo(methodCode)
                if (video != null) {
                    _uiState.update { if (it.problem?.id == problemId) it.copy(solutionVideo = video) else it }
                }
            }
        }

        /**
         * 오답 노트에서 넘어온 특정 문제 하나를 복습 모드로 연다 — 추천을 거치지 않고 그 문제를 그대로.
         * 재풀이 기록은 복습 시도(reviewMode)로 남겨 추천 난이도에 영향을 주지 않는다.
         */
        private fun loadReview(problemId: String) {
            _uiState.update { it.copy(phase = SolvePhase.LOADING, selectedIndex = null, result = null) }
            viewModelScope.launch {
                val problem = getProblemById(problemId)
                if (problem == null) {
                    _uiState.update { it.copy(phase = SolvePhase.EMPTY) }
                    return@launch
                }
                questionStartMillis = clock.nowMillis()
                _uiState.update { current ->
                    current.copy(
                        phase = SolvePhase.SOLVING,
                        reviewMode = true,
                        problem = problem,
                        area = problem.area,
                        difficulty = problem.difficulty,
                        selectedIndex = null,
                        result = null,
                        showExplanation = false,
                        reason = RecommendationReason.REVIEW,
                        solutionVideo = null,
                        dissectionAssignment = emptyMap(),
                        dissectionPiece = 0,
                        dissectionResult = null,
                    )
                }
                fillSolutionVideo(problem.id, problem.methodCode)
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
                    timestampMillis = clock.nowMillis(),
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
            if (current.phase != SolvePhase.SOLVING || submitting) return
            submitting = true

            viewModelScope.launch {
                try {
                    val gradingResult =
                        submitAnswer(
                            problem = problem,
                            selectedIndex = selected,
                            timeSpentSec = elapsedOnQuestionSec(),
                            timestamp = clock.nowMillis(),
                            reviewMode = current.reviewMode,
                        )
                    _uiState.update {
                        it.copy(
                            phase = SolvePhase.GRADED,
                            sessionElapsedSec = sessionElapsedSec(),
                            goalJustReached = it.problemOrdinal == it.dailyGoal,
                            result = gradingResult,
                            retryLikely =
                                !gradingResult.isCorrect && it.sessionStreak >= 1 && !it.reviewMode,
                            sessionStreak = if (gradingResult.isCorrect) it.sessionStreak + 1 else 0,
                        )
                    }
                } finally {
                    submitting = false
                }
            }
        }

        /**
         * "모르겠어요" — 답을 고르지 않고 풀이를 본다. 오답으로 기록해 난이도가 자연스럽게 내려가고
         * 오답 노트에 담긴다(다음에 다시 학습). 결과 시트가 정답·풀이와 함께 열린다.
         */
        fun giveUp() {
            val current = _uiState.value
            val problem = current.problem ?: return
            if (current.phase != SolvePhase.SOLVING || submitting) return
            submitting = true

            viewModelScope.launch {
                try {
                    val gradingResult =
                        submitGiveUp(
                            problem = problem,
                            timeSpentSec = elapsedOnQuestionSec(),
                            timestamp = clock.nowMillis(),
                            reviewMode = current.reviewMode,
                        )
                    _uiState.update {
                        it.copy(
                            phase = SolvePhase.GRADED,
                            sessionElapsedSec = sessionElapsedSec(),
                            goalJustReached = it.problemOrdinal == it.dailyGoal,
                            result = gradingResult,
                            retryLikely = false,
                            sessionStreak = 0,
                        )
                    }
                } finally {
                    submitting = false
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
                s.copy(dissectionAssignment = next, dissectionResult = null)
            }
        }

        fun clearDissection() {
            if (_uiState.value.phase != SolvePhase.SOLVING) return
            // 힌트도 함께 지운다 — 안 그러면 다 칠한 뒤에도 "아직 안 칠한 칸이 있어요"가 남는다.
            _uiState.update { it.copy(dissectionAssignment = emptyMap(), dissectionResult = null) }
        }

        fun submitDissection() {
            val current = _uiState.value
            val puzzle = current.problem?.dissection ?: return
            if (current.phase != SolvePhase.SOLVING || submitting) return
            // 미완성(칸을 다 안 채움)은 실제 답이 아니므로 시도 기록 없이 힌트만 — 계속 풀 수 있게 SOLVING 유지.
            if (current.dissectionAssignment.keys != puzzle.cells.toSet()) {
                _uiState.update { it.copy(dissectionResult = DissectionValidation(false, DissectionError.INCOMPLETE)) }
                return
            }
            val problem = current.problem
            submitting = true
            viewModelScope.launch {
                try {
                    val validation =
                        submitDissection(
                            problem = problem,
                            assignment = current.dissectionAssignment,
                            timeSpentSec = elapsedOnQuestionSec(),
                            timestamp = clock.nowMillis(),
                            reviewMode = current.reviewMode,
                        )
                    _uiState.update {
                        it.copy(
                            phase = SolvePhase.GRADED,
                            sessionElapsedSec = sessionElapsedSec(),
                            goalJustReached = it.problemOrdinal == it.dailyGoal,
                            dissectionResult = validation,
                            sessionStreak = if (validation.isValid) it.sessionStreak + 1 else 0,
                        )
                    }
                } finally {
                    submitting = false
                }
            }
        }

        /**
         * 이 문항에 쓴 시간(초). 상한 필수 — 문제를 열어둔 채 기기가 잠들면(저녁·밤새) 경과 시간이
         * 통째로 기록돼 평균 통계를 영구히 왜곡한다. 사고력 문제 기준 30분이면 충분히 관대한 상한.
         */
        private fun elapsedOnQuestionSec(): Int =
            ((clock.nowMillis() - questionStartMillis) / MILLIS_PER_SECOND)
                .toInt()
                .coerceIn(0, Attempt.MAX_TIME_SPENT_SEC)

        private fun sessionElapsedSec(): Int = ((clock.nowMillis() - sessionStartMillis) / MILLIS_PER_SECOND).toInt().coerceAtLeast(0)

        companion object {
            const val MILLIS_PER_SECOND = 1000L

            /** 오답 노트 → 복습 라우트가 넘겨주는 문제 id 인자 키. */
            const val ARG_REVIEW_PROBLEM_ID = "reviewProblemId"
        }
    }
