package com.ddakpul.math.domain.usecase

import com.ddakpul.math.core.common.AppError
import com.ddakpul.math.core.common.AppResult
import com.ddakpul.math.data.FakeEntitlementRepository
import com.ddakpul.math.data.FakeLearnerRepository
import com.ddakpul.math.data.FakeProblemFeedbackRepository
import com.ddakpul.math.data.FakeProblemRepository
import com.ddakpul.math.domain.model.Monetization
import com.ddakpul.math.domain.model.RecommendationReason
import com.ddakpul.math.domain.usecase.TestFixtures.attempt
import com.ddakpul.math.domain.usecase.TestFixtures.standardGroups
import com.google.common.truth.Truth.assertThat
import kotlinx.coroutines.test.runTest
import org.junit.Test

class GetNextProblemUseCaseTest {
    private fun useCase(
        learner: FakeLearnerRepository,
        problems: FakeProblemRepository = FakeProblemRepository(standardGroups()),
        feedback: FakeProblemFeedbackRepository = FakeProblemFeedbackRepository(),
        entitlement: FakeEntitlementRepository = FakeEntitlementRepository(),
    ) = GetNextProblemUseCase(
        getActiveGroups = GetActiveProblemGroupsUseCase(problems, feedback),
        learnerRepository = learner,
        entitlementRepository = entitlement,
        recommend = RecommendNextProblemUseCase(),
        computeReviewQueue = ComputeReviewQueueUseCase(),
    )

    @Test
    fun emptyProblemBank_returnsFailure() =
        runTest {
            val useCase = useCase(FakeLearnerRepository(), FakeProblemRepository(emptyList()))

            val result = useCase(todaySolved = 0, zoneOffsetMillis = 0L, nowMillis = 0L)

            assertThat(result).isInstanceOf(AppResult.Failure::class.java)
            assertThat((result as AppResult.Failure).error).isEqualTo(AppError.EmptyProblemBank)
        }

    @Test
    fun noHistory_succeedsWithoutChangingDifficulty() =
        runTest {
            val learner = FakeLearnerRepository(initialDifficulty = 3)

            val result = useCase(learner)(todaySolved = 0, zoneOffsetMillis = 0L, nowMillis = 0L)

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

            val result = useCase(learner)(todaySolved = 0, zoneOffsetMillis = 0L, nowMillis = 0L)

            assertThat((result as AppResult.Success).data.targetDifficulty).isEqualTo(4)
            assertThat(learner.currentDifficulty).isEqualTo(4)
            assertThat(learner.setDifficultyCallCount).isEqualTo(1)
        }

    @Test
    fun reviewSlot_servesDueReview_withoutPersistingDifficulty() =
        runTest {
            val learner = FakeLearnerRepository(initialDifficulty = 3)
            // 10일차에 d2 그룹 숙달(연속 2정답) → 만기 11일차.
            learner.recordAttempt(attempt("d2-1", true, timestamp = DAY * 10))
            learner.recordAttempt(attempt("d2-2", true, timestamp = DAY * 10 + HOUR))

            // 12일차, 오늘 이미 2문제 풀어 3번째가 복습 슬롯.
            val result =
                useCase(learner)(todaySolved = 2, zoneOffsetMillis = 0L, nowMillis = DAY * 12)

            val recommendation = (result as AppResult.Success).data
            assertThat(recommendation.reason).isEqualTo(RecommendationReason.REVIEW)
            assertThat(recommendation.group.id).isEqualTo("g-2")
            // 복습은 현재 난이도를 바꾸지 않는다.
            assertThat(recommendation.targetDifficulty).isEqualTo(3)
            assertThat(learner.setDifficultyCallCount).isEqualTo(0)
        }

    @Test
    fun excludedProblem_isNeverRecommended() =
        runTest {
            val learner = FakeLearnerRepository(initialDifficulty = 3)
            val feedback = FakeProblemFeedbackRepository()
            // 난이도 3 그룹의 문제 3개 중 2개를 제외하면 남은 1개만 나올 수 있다.
            feedback.exclude("d3-1", reason = null, timestampMillis = 0L)
            feedback.exclude("d3-2", reason = null, timestampMillis = 1L)

            repeat(20) {
                val result =
                    useCase(learner, feedback = feedback)(
                        todaySolved = 0,
                        zoneOffsetMillis = 0L,
                        nowMillis = 0L,
                    )
                val recommended = (result as AppResult.Success).data.problem
                assertThat(recommended.id).isEqualTo("d3-3")
            }
        }

    @Test
    fun allProblemsExcluded_returnsEmptyProblemBank() =
        runTest {
            val learner = FakeLearnerRepository(initialDifficulty = 3)
            val feedback = FakeProblemFeedbackRepository()
            standardGroups().flatMap { it.problems }.forEachIndexed { index, problem ->
                feedback.exclude(problem.id, reason = null, timestampMillis = index.toLong())
            }

            val result =
                useCase(learner, feedback = feedback)(
                    todaySolved = 0,
                    zoneOffsetMillis = 0L,
                    nowMillis = 0L,
                )

            assertThat(result).isInstanceOf(AppResult.Failure::class.java)
            assertThat((result as AppResult.Failure).error).isEqualTo(AppError.EmptyProblemBank)
        }

    @Test
    fun freeUser_isCappedAtFreeMaxDifficulty_andSuggestsPremium() =
        runTest {
            val learner = FakeLearnerRepository(initialDifficulty = 3)
            // 난이도 3에서 2연속 정답 → 추천기는 4로 올리려 한다.
            learner.recordAttempt(attempt("d3-1", true))
            learner.recordAttempt(attempt("d3-2", true))

            val result =
                useCase(learner, entitlement = FakeEntitlementRepository(premium = false))(
                    todaySolved = 0,
                    zoneOffsetMillis = 0L,
                    // 출시 기념 무료 기간이 지난 시점 — 진짜 무료(게이트 적용) 동작을 검증.
                    nowMillis = Monetization.LAUNCH_FREE_UNTIL_MILLIS,
                )

            val rec = (result as AppResult.Success).data
            // 무료는 난이도 상한으로 고정되고, 승급 대신 페이월을 권한다.
            assertThat(rec.targetDifficulty).isEqualTo(Monetization.FREE_MAX_DIFFICULTY)
            assertThat(rec.premiumSuggested).isTrue()
            assertThat(rec.problem.difficulty).isAtMost(Monetization.FREE_MAX_DIFFICULTY)
            // 상한에 그대로 머무르므로 난이도 저장은 일어나지 않는다.
            assertThat(learner.setDifficultyCallCount).isEqualTo(0)
        }

    @Test
    fun freeUser_duringLaunchPromo_getsFullAccessAndPromotes() =
        runTest {
            val learner = FakeLearnerRepository(initialDifficulty = 3)
            learner.recordAttempt(attempt("d3-1", true))
            learner.recordAttempt(attempt("d3-2", true))

            // 무료 사용자라도 출시 기념 무료 기간(마감 직전) 동안엔 상한 없이 승급한다.
            val result =
                useCase(learner, entitlement = FakeEntitlementRepository(premium = false))(
                    todaySolved = 0,
                    zoneOffsetMillis = 0L,
                    nowMillis = Monetization.LAUNCH_FREE_UNTIL_MILLIS - 1L,
                )

            val rec = (result as AppResult.Success).data
            assertThat(rec.targetDifficulty).isEqualTo(4)
            assertThat(rec.premiumSuggested).isFalse()
        }

    @Test
    fun premiumUser_promotesPastFreeCap() =
        runTest {
            val learner = FakeLearnerRepository(initialDifficulty = 3)
            learner.recordAttempt(attempt("d3-1", true))
            learner.recordAttempt(attempt("d3-2", true))

            val result =
                useCase(learner, entitlement = FakeEntitlementRepository(premium = true))(
                    todaySolved = 0,
                    zoneOffsetMillis = 0L,
                    nowMillis = 0L,
                )

            val rec = (result as AppResult.Success).data
            assertThat(rec.targetDifficulty).isEqualTo(4)
            assertThat(rec.premiumSuggested).isFalse()
            assertThat(learner.currentDifficulty).isEqualTo(4)
        }

    @Test
    fun freeUser_belowCap_isNotSuggestedPremium() =
        runTest {
            val learner = FakeLearnerRepository(initialDifficulty = 2)
            // 혼조(맞았다 틀렸다) → 난이도 2 유지, 상한 아래.
            learner.recordAttempt(attempt("d2-1", true))
            learner.recordAttempt(attempt("d2-2", false))

            val result =
                useCase(learner, entitlement = FakeEntitlementRepository(premium = false))(
                    todaySolved = 0,
                    zoneOffsetMillis = 0L,
                    // 출시 기념 무료 기간이 지난 시점 — 진짜 무료(게이트 적용) 동작을 검증.
                    nowMillis = Monetization.LAUNCH_FREE_UNTIL_MILLIS,
                )

            val rec = (result as AppResult.Success).data
            assertThat(rec.premiumSuggested).isFalse()
            assertThat(rec.problem.difficulty).isAtMost(Monetization.FREE_MAX_DIFFICULTY)
        }

    private companion object {
        const val HOUR = 3_600_000L
        const val DAY = 86_400_000L
    }
}
