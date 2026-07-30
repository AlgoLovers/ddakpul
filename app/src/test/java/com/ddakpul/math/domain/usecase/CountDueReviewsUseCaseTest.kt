package com.ddakpul.math.domain.usecase

import com.ddakpul.math.data.FakeLearnerRepository
import com.ddakpul.math.data.FakeProblemFeedbackRepository
import com.ddakpul.math.data.FakeProblemRepository
import com.ddakpul.math.domain.usecase.TestFixtures.attempt
import com.ddakpul.math.domain.usecase.TestFixtures.standardGroups
import com.google.common.truth.Truth.assertThat
import kotlinx.coroutines.test.runTest
import org.junit.Test

class CountDueReviewsUseCaseTest {
    private val dayMillis = 24 * 60 * 60 * 1000L

    private fun useCase(
        learner: FakeLearnerRepository,
        problems: FakeProblemRepository = FakeProblemRepository(standardGroups()),
    ) = CountDueReviewsUseCase(
        getActiveGroups = GetActiveProblemGroupsUseCase(problems, FakeProblemFeedbackRepository()),
        learnerRepository = learner,
        computeReviewQueue = ComputeReviewQueueUseCase(),
    )

    @Test
    fun noAttempts_returnsZero() =
        runTest {
            val count = useCase(FakeLearnerRepository())(zoneOffsetMillis = 0L, nowMillis = 0L)

            assertThat(count).isEqualTo(0)
        }

    @Test
    fun emptyProblemBank_returnsZero() =
        runTest {
            val learner = FakeLearnerRepository()
            learner.recordAttempt(attempt("d3-1", true))

            val count =
                useCase(learner, FakeProblemRepository(emptyList()))(zoneOffsetMillis = 0L, nowMillis = 0L)

            assertThat(count).isEqualTo(0)
        }

    @Test
    fun masteredGroup_dueAfterInterval_isCounted() =
        runTest {
            val learner = FakeLearnerRepository()
            // 연속 2정답 → 숙달(박스1, 만기 1일 뒤). 이틀 뒤 시점이면 만기 지남.
            learner.recordAttempt(attempt("d3-1", true, timestamp = 0L))
            learner.recordAttempt(attempt("d3-2", true, timestamp = 0L))

            val count = useCase(learner)(zoneOffsetMillis = 0L, nowMillis = 2 * dayMillis)

            assertThat(count).isEqualTo(1)
        }

    @Test
    fun masteredGroup_beforeDue_returnsZero() =
        runTest {
            val learner = FakeLearnerRepository()
            learner.recordAttempt(attempt("d3-1", true, timestamp = 0L))
            learner.recordAttempt(attempt("d3-2", true, timestamp = 0L))

            // 숙달 당일(만기 전)은 아직 복습 대상이 아니다.
            val count = useCase(learner)(zoneOffsetMillis = 0L, nowMillis = 0L)

            assertThat(count).isEqualTo(0)
        }
}
