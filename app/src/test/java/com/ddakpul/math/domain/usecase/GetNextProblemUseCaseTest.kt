package com.ddakpul.math.domain.usecase

import com.ddakpul.math.core.common.AppError
import com.ddakpul.math.core.common.AppResult
import com.ddakpul.math.data.FakeLearnerRepository
import com.ddakpul.math.data.FakeProblemRepository
import com.ddakpul.math.domain.usecase.TestFixtures.attempt
import com.ddakpul.math.domain.usecase.TestFixtures.standardGroups
import com.google.common.truth.Truth.assertThat
import kotlinx.coroutines.test.runTest
import org.junit.Test

class GetNextProblemUseCaseTest {
    private val recommend = RecommendNextProblemUseCase()

    @Test
    fun emptyProblemBank_returnsFailure() =
        runTest {
            val useCase =
                GetNextProblemUseCase(
                    problemRepository = FakeProblemRepository(emptyList()),
                    learnerRepository = FakeLearnerRepository(),
                    recommend = recommend,
                )

            val result = useCase()

            assertThat(result).isInstanceOf(AppResult.Failure::class.java)
            assertThat((result as AppResult.Failure).error).isEqualTo(AppError.EmptyProblemBank)
        }

    @Test
    fun noHistory_succeedsWithoutChangingDifficulty() =
        runTest {
            val learner = FakeLearnerRepository(initialDifficulty = 3)
            val useCase =
                GetNextProblemUseCase(
                    problemRepository = FakeProblemRepository(standardGroups()),
                    learnerRepository = learner,
                    recommend = recommend,
                )

            val result = useCase()

            assertThat(result).isInstanceOf(AppResult.Success::class.java)
            assertThat((result as AppResult.Success).data.targetDifficulty).isEqualTo(3)
            // 난이도 변화가 없으므로 저장은 호출되지 않는다.
            assertThat(learner.setDifficultyCallCount).isEqualTo(0)
        }

    @Test
    fun promotion_persistsNewDifficulty() =
        runTest {
            val learner = FakeLearnerRepository(initialDifficulty = 3)
            // 최근 2연속 정답을 미리 기록해 승급 조건을 만든다.
            learner.recordAttempt(attempt("d3-1", true))
            learner.recordAttempt(attempt("d3-2", true))

            val useCase =
                GetNextProblemUseCase(
                    problemRepository = FakeProblemRepository(standardGroups()),
                    learnerRepository = learner,
                    recommend = recommend,
                )

            val result = useCase()

            assertThat((result as AppResult.Success).data.targetDifficulty).isEqualTo(4)
            assertThat(learner.currentDifficulty).isEqualTo(4)
            assertThat(learner.setDifficultyCallCount).isEqualTo(1)
        }
}
