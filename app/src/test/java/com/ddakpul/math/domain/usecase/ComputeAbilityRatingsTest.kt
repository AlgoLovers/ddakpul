package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.model.AbilityRating
import com.ddakpul.math.domain.model.MathArea
import com.ddakpul.math.domain.usecase.TestFixtures.attempt
import com.ddakpul.math.domain.usecase.TestFixtures.group
import com.ddakpul.math.domain.usecase.TestFixtures.problem
import com.google.common.truth.Truth.assertThat
import org.junit.Test

/** replay 기반 θ 복원(ComputeAbilityRatings)의 성질을 고정한다. */
class ComputeAbilityRatingsTest {
    private val groups =
        listOf(
            group(
                difficulty = 2,
                problems = (1..3).map { problem("n$it", 2, groupId = "g-n") },
                id = "g-n",
            ),
            group(
                difficulty = 2,
                problems = (1..3).map { problem("s$it", 2, groupId = "g-s", area = MathArea.SHAPE_MEASUREMENT) },
                id = "g-s",
                area = MathArea.SHAPE_MEASUREMENT,
            ),
        )

    private val initial = AbilityRating(rating = EloLite.INITIAL_ABILITY_RATING, attemptCount = 0)

    @Test
    fun emptyHistory_returnsInitialThetaForAllAreas() {
        val ratings = computeAbilityRatings(emptyList(), groups)

        assertThat(ratings.keys).containsExactlyElementsIn(MathArea.entries)
        MathArea.entries.forEach { area ->
            assertThat(ratings.getValue(area)).isEqualTo(initial)
        }
    }

    @Test
    fun correctAttempt_raisesTheta() {
        val ratings = computeAbilityRatings(listOf(attempt("n1", isCorrect = true)), groups)

        assertThat(ratings.getValue(MathArea.NUMBER_OPERATION).rating).isGreaterThan(initial.rating)
    }

    @Test
    fun wrongAttempt_lowersTheta() {
        val ratings = computeAbilityRatings(listOf(attempt("n1", isCorrect = false)), groups)

        assertThat(ratings.getValue(MathArea.NUMBER_OPERATION).rating).isLessThan(initial.rating)
    }

    @Test
    fun repeatedCorrectAnswers_convergeThenStabilize() {
        // 같은 난이도만 100번 연속 정답: θ는 오르다가, 기대정답률이 캡에 닿으면 더는 움직이지 않는다.
        val attempts = (1..100).map { n -> attempt("n${n % 3 + 1}", isCorrect = true, timestamp = n.toLong()) }

        val after99 = computeAbilityRatings(attempts.take(99), groups).getValue(MathArea.NUMBER_OPERATION)
        val after100 = computeAbilityRatings(attempts, groups).getValue(MathArea.NUMBER_OPERATION)

        assertThat(after100.rating).isGreaterThan(initial.rating)
        assertThat(after100.rating).isEqualTo(after99.rating) // 수렴 후 안정
    }

    @Test
    fun kDecay_earlyAttemptsMoveThetaMoreThanLateAttempts() {
        val attempts = (1..60).map { n -> attempt("n${n % 3 + 1}", isCorrect = true, timestamp = n.toLong()) }
        val trajectory =
            (0..60).map { count ->
                computeAbilityRatings(attempts.take(count), groups).getValue(MathArea.NUMBER_OPERATION).rating
            }

        val placementDelta = trajectory[1] - trajectory[0] // 1번째 시도(K 최대)
        val stableDelta = trajectory[EloLite.DEVELOPING_ATTEMPTS + 5] - trajectory[EloLite.DEVELOPING_ATTEMPTS + 4]

        assertThat(placementDelta).isGreaterThan(stableDelta)
    }

    @Test
    fun areaIndependence_attemptsInOneAreaNeverTouchOthers() {
        val attempts =
            listOf(
                attempt("n1", isCorrect = true),
                attempt("n2", isCorrect = false),
                attempt("n3", isCorrect = true),
            )

        val ratings = computeAbilityRatings(attempts, groups)

        assertThat(ratings.getValue(MathArea.SHAPE_MEASUREMENT)).isEqualTo(initial)
        assertThat(ratings.getValue(MathArea.CHANGE_RELATION)).isEqualTo(initial)
        assertThat(ratings.getValue(MathArea.DATA_POSSIBILITY)).isEqualTo(initial)
    }

    @Test
    fun replayIsDeterministic_sameHistorySameRatings() {
        val attempts =
            listOf(
                attempt("n1", isCorrect = true),
                attempt("s1", isCorrect = false),
                attempt("n2", isCorrect = true),
                attempt("s2", isCorrect = true),
                attempt("n3", isCorrect = false),
            )

        val first = computeAbilityRatings(attempts, groups)
        val second = computeAbilityRatings(attempts, groups)

        assertThat(first).isEqualTo(second)
    }

    @Test
    fun attemptsOnUnknownProblems_areIgnored() {
        val attempts =
            listOf(
                attempt("ghost1", isCorrect = true),
                attempt("ghost2", isCorrect = false),
            )

        val ratings = computeAbilityRatings(attempts, groups)

        MathArea.entries.forEach { area ->
            assertThat(ratings.getValue(area)).isEqualTo(initial)
        }
    }

    @Test
    fun attemptCount_tracksPerArea() {
        val attempts =
            listOf(
                attempt("n1", isCorrect = true),
                attempt("n2", isCorrect = false),
                attempt("s1", isCorrect = true),
            )

        val ratings = computeAbilityRatings(attempts, groups)

        assertThat(ratings.getValue(MathArea.NUMBER_OPERATION).attemptCount).isEqualTo(2)
        assertThat(ratings.getValue(MathArea.SHAPE_MEASUREMENT).attemptCount).isEqualTo(1)
        assertThat(ratings.getValue(MathArea.CHANGE_RELATION).attemptCount).isEqualTo(0)
        assertThat(ratings.getValue(MathArea.DATA_POSSIBILITY).attemptCount).isEqualTo(0)
    }
}
