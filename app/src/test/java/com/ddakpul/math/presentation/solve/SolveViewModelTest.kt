package com.ddakpul.math.presentation.solve

import androidx.lifecycle.SavedStateHandle
import com.ddakpul.math.data.FakeLearnerRepository
import com.ddakpul.math.data.FakeProblemFeedbackRepository
import com.ddakpul.math.data.FakeProblemRepository
import com.ddakpul.math.data.FakeSolutionVideoRepository
import com.ddakpul.math.domain.model.Attempt
import com.ddakpul.math.domain.time.FakeClock
import com.ddakpul.math.domain.usecase.ComputeReviewQueueUseCase
import com.ddakpul.math.domain.usecase.ExcludeProblemUseCase
import com.ddakpul.math.domain.usecase.GetActiveProblemGroupsUseCase
import com.ddakpul.math.domain.usecase.GetNextProblemUseCase
import com.ddakpul.math.domain.usecase.GetProblemByIdUseCase
import com.ddakpul.math.domain.usecase.GradeAttemptUseCase
import com.ddakpul.math.domain.usecase.ObserveDailyGoalUseCase
import com.ddakpul.math.domain.usecase.ObserveLearningStatsUseCase
import com.ddakpul.math.domain.usecase.RecommendNextProblemUseCase
import com.ddakpul.math.domain.usecase.SubmitAnswerUseCase
import com.ddakpul.math.domain.usecase.SubmitDissectionUseCase
import com.ddakpul.math.domain.usecase.SubmitGiveUpUseCase
import com.ddakpul.math.domain.usecase.TestFixtures
import com.ddakpul.math.domain.usecase.ValidateDissectionUseCase
import com.google.common.truth.Truth.assertThat
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.test.UnconfinedTestDispatcher
import kotlinx.coroutines.test.resetMain
import kotlinx.coroutines.test.runTest
import kotlinx.coroutines.test.setMain
import org.junit.After
import org.junit.Before
import org.junit.Test

/**
 * 풀이 화면의 상태 전이 검증. [FakeClock] 덕분에 "문항을 30분 넘게 열어둔" 같은 시간 의존
 * 시나리오를 실제로 기다리지 않고 재현할 수 있다.
 */
class SolveViewModelTest {
    private val dispatcher = UnconfinedTestDispatcher()
    private lateinit var learner: FakeLearnerRepository
    private lateinit var clock: FakeClock

    @Before
    fun setUp() {
        Dispatchers.setMain(dispatcher)
        learner = FakeLearnerRepository()
        clock = FakeClock(now = START_MILLIS)
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
    }

    private fun viewModel(reviewProblemId: String? = null): SolveViewModel {
        val problems = FakeProblemRepository(TestFixtures.standardGroups())
        val feedback = FakeProblemFeedbackRepository()
        val activeGroups = GetActiveProblemGroupsUseCase(problems, feedback)
        return SolveViewModel(
            getNextProblem =
                GetNextProblemUseCase(
                    getActiveGroups = activeGroups,
                    learnerRepository = learner,
                    recommend = RecommendNextProblemUseCase(),
                    computeReviewQueue = ComputeReviewQueueUseCase(),
                ),
            getProblemById = GetProblemByIdUseCase(problems),
            submitAnswer = SubmitAnswerUseCase(learner, GradeAttemptUseCase()),
            submitDissection = SubmitDissectionUseCase(learner, ValidateDissectionUseCase()),
            submitGiveUp = SubmitGiveUpUseCase(learner),
            excludeProblem = ExcludeProblemUseCase(feedback),
            solutionVideoRepository = FakeSolutionVideoRepository(),
            observeStats = ObserveLearningStatsUseCase(learner, problems),
            observeDailyGoal = ObserveDailyGoalUseCase(learner),
            clock = clock,
            savedStateHandle =
                SavedStateHandle(
                    reviewProblemId?.let { mapOf(SolveViewModel.ARG_REVIEW_PROBLEM_ID to it) } ?: emptyMap(),
                ),
        )
    }

    private suspend fun SolveViewModel.awaitSolving(): SolveUiState = uiState.first { it.phase == SolvePhase.SOLVING }

    @Test
    fun `제출을 연타해도 시도는 한 번만 기록된다`() =
        runTest {
            val vm = viewModel()
            vm.awaitSolving()

            vm.selectChoice(0)
            vm.submit()
            vm.submit()
            vm.uiState.first { it.phase == SolvePhase.GRADED }

            assertThat(learner.recordedAttempts).hasSize(1)
        }

    @Test
    fun `문항을 오래 열어두면 기록 시간이 상한으로 잘린다`() =
        runTest {
            val vm = viewModel()
            vm.awaitSolving()

            // 문제를 연 채 기기가 밤새 잠든 상황 — 상한이 없으면 평균 시간 통계가 영구히 왜곡된다.
            clock.advance(HOURS_8_MILLIS)
            vm.selectChoice(0)
            vm.submit()
            vm.uiState.first { it.phase == SolvePhase.GRADED }

            assertThat(learner.recordedAttempts.single().timeSpentSec).isEqualTo(Attempt.MAX_TIME_SPENT_SEC)
        }

    @Test
    fun `실제로 걸린 시간은 그대로 기록된다`() =
        runTest {
            val vm = viewModel()
            vm.awaitSolving()

            clock.advance(90_000L)
            vm.selectChoice(0)
            vm.submit()
            vm.uiState.first { it.phase == SolvePhase.GRADED }

            assertThat(learner.recordedAttempts.single().timeSpentSec).isEqualTo(90)
        }

    @Test
    fun `모르겠어요는 오답으로 기록되고 고른 답 없이 풀이가 열린다`() =
        runTest {
            val vm = viewModel()
            vm.awaitSolving()

            vm.giveUp()
            val graded = vm.uiState.first { it.phase == SolvePhase.GRADED }

            assertThat(learner.recordedAttempts.single().isCorrect).isFalse()
            assertThat(graded.result?.selectedIndex).isNull()
            assertThat(graded.result?.isCorrect).isFalse()
        }

    @Test
    fun `오답 노트에서 연 문제는 복습 시도로 기록된다`() =
        runTest {
            val vm = viewModel(reviewProblemId = "d3-1")
            val solving = vm.awaitSolving()
            assertThat(solving.problem?.id).isEqualTo("d3-1")
            assertThat(solving.reviewMode).isTrue()

            vm.selectChoice(0)
            vm.submit()
            vm.uiState.first { it.phase == SolvePhase.GRADED }

            assertThat(learner.recordedAttempts.single().reviewMode).isTrue()
        }

    /**
     * 회귀 방지: 연타 가드(`submitting`)를 채점 후 내리지 않으면 첫 제출 이후 이 화면의 모든
     * 제출이 영구히 막힌다 — 두 번째 문제부터 답을 낼 수 없게 된다(v1.0.0에 실재했던 버그).
     */
    @Test
    fun `다음 문제에서도 다시 제출할 수 있다`() =
        runTest {
            val vm = viewModel()
            vm.awaitSolving()
            vm.selectChoice(0)
            vm.submit()
            vm.uiState.first { it.phase == SolvePhase.GRADED }

            vm.loadNext()
            vm.awaitSolving()
            vm.selectChoice(0)
            vm.submit()
            vm.uiState.first { it.phase == SolvePhase.GRADED }

            assertThat(learner.recordedAttempts).hasSize(2)
        }

    @Test
    fun `정답을 이어 맞히면 세션 연속 정답이 쌓이고 오답에서 끊긴다`() =
        runTest {
            val vm = viewModel()
            vm.awaitSolving()

            vm.selectChoice(CORRECT_INDEX)
            vm.submit()
            assertThat(vm.uiState.first { it.phase == SolvePhase.GRADED }.sessionStreak).isEqualTo(1)

            vm.loadNext()
            vm.awaitSolving()
            vm.selectChoice(WRONG_INDEX)
            vm.submit()
            assertThat(vm.uiState.first { it.phase == SolvePhase.GRADED }.sessionStreak).isEqualTo(0)
        }

    private companion object {
        /** 2026-01-01 00:00 UTC — 특정 날짜에 의존하지 않되 epoch 0의 경계 효과는 피한다. */
        const val START_MILLIS = 1_767_225_600_000L
        const val HOURS_8_MILLIS = 8L * 60 * 60 * 1000
        const val CORRECT_INDEX = 0
        const val WRONG_INDEX = 1
    }
}
