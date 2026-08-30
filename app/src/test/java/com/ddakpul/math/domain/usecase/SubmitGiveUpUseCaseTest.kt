package com.ddakpul.math.domain.usecase

import com.ddakpul.math.data.FakeLearnerRepository
import com.ddakpul.math.domain.usecase.TestFixtures.problem
import com.google.common.truth.Truth.assertThat
import kotlinx.coroutines.test.runTest
import org.junit.Test

class SubmitGiveUpUseCaseTest {
    private val learner = FakeLearnerRepository()
    private val submit = SubmitGiveUpUseCase(RecordAttemptUseCase(learner))

    private val problem =
        problem(id = "p-giveup", difficulty = 3, answerIndex = 2, explanation = "이렇게 푼다")

    @Test
    fun recordsWrongAttempt_andReturnsSolutionWithoutSelection() =
        runTest {
            val result = submit(problem, timeSpentSec = 45, timestamp = 1_000L)

            // 못 푼 것이므로 오답으로 기록된다(난이도 하강·오답 노트 편입의 근거).
            assertThat(learner.recordedAttempts).hasSize(1)
            val attempt = learner.recordedAttempts.first()
            assertThat(attempt.isCorrect).isFalse()
            assertThat(attempt.problemId).isEqualTo("p-giveup")
            assertThat(attempt.reviewMode).isFalse()

            // 고른 답은 없고(selectedIndex=null), 정답과 풀이는 함께 돌려준다.
            assertThat(result.isCorrect).isFalse()
            assertThat(result.selectedIndex).isNull()
            assertThat(result.correctIndex).isEqualTo(2)
            assertThat(result.mistake).isNull()
            assertThat(result.explanation).isEqualTo("이렇게 푼다")
        }

    @Test
    fun reviewMode_flagsAttemptAsReview() =
        runTest {
            submit(problem, timeSpentSec = 10, timestamp = 2_000L, reviewMode = true)

            assertThat(learner.recordedAttempts.first().reviewMode).isTrue()
        }
}
