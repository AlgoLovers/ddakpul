package com.ddakpul.math.domain.usecase

import com.ddakpul.math.data.FakeLearnerRepository
import com.ddakpul.math.domain.usecase.TestFixtures.problem
import com.google.common.truth.Truth.assertThat
import kotlinx.coroutines.test.runTest
import org.junit.Test

class SubmitAnswerUseCaseTest {
    @Test
    fun correctAnswer_gradesAndRecordsAttempt() =
        runTest {
            val learner = FakeLearnerRepository()
            val useCase = SubmitAnswerUseCase(learner, GradeAttemptUseCase())
            val problem = problem(id = "p1", difficulty = 2, answerIndex = 1)

            val result =
                useCase(
                    problem = problem,
                    selectedIndex = 1,
                    timeSpentSec = 12,
                    timestamp = 1_000L,
                )

            assertThat(result.isCorrect).isTrue()
            assertThat(learner.recordedAttempts).hasSize(1)
            with(learner.recordedAttempts.first()) {
                assertThat(problemId).isEqualTo("p1")
                assertThat(isCorrect).isTrue()
                assertThat(timeSpentSec).isEqualTo(12)
                assertThat(timestamp).isEqualTo(1_000L)
            }
        }

    @Test
    fun wrongAnswer_recordsIncorrectAttempt() =
        runTest {
            val learner = FakeLearnerRepository()
            val useCase = SubmitAnswerUseCase(learner, GradeAttemptUseCase())
            val problem = problem(id = "p2", difficulty = 2, answerIndex = 0)

            val result = useCase(problem, selectedIndex = 3, timeSpentSec = 5, timestamp = 2_000L)

            assertThat(result.isCorrect).isFalse()
            assertThat(learner.recordedAttempts.first().isCorrect).isFalse()
        }
}
