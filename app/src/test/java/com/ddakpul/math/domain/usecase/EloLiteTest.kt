package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.model.Difficulty
import com.google.common.truth.Truth.assertThat
import org.junit.Test
import kotlin.math.abs

/** Elo-lite 산술 코어(룩업테이블·K 스케줄·갱신 공식)의 성질을 고정한다. */
class EloLiteTest {
    @Test
    fun expectedScore_evenMatch_isExactlyHalf() {
        assertThat(EloLite.expectedScorePermille(0)).isEqualTo(EloLite.PERMILLE / 2)
    }

    @Test
    fun expectedScore_symmetricPairs_sumToWhole() {
        // E(+d) + E(−d) = 1000‰ — 구간 경계·내부·캡 영역을 두루 찍는다.
        listOf(0, 1, 13, 25, 74, 137, 300, 324, 449, 512, 899, 900, 1_000, 4_000).forEach { diff ->
            val sum = EloLite.expectedScorePermille(diff) + EloLite.expectedScorePermille(-diff)
            assertThat(sum).isEqualTo(EloLite.PERMILLE)
        }
    }

    @Test
    fun expectedScore_neverDecreasesWithAdvantage() {
        var previous = EloLite.expectedScorePermille(-1_201)
        (-1_200..1_200).forEach { diff ->
            val expected = EloLite.expectedScorePermille(diff)
            assertThat(expected).isAtLeast(previous)
            previous = expected
        }
    }

    @Test
    fun expectedScore_atTargetGap_matchesEightyFivePercentRule() {
        // 목표 레이팅차(300)에서 기대정답률이 85% 규칙의 목표(850‰)에 거의 정확히 닿아야 한다.
        val atTargetGap = EloLite.expectedScorePermille(EloLite.TARGET_RATING_GAP)
        assertThat(abs(atTargetGap - EloLite.TARGET_SUCCESS_PERMILLE)).isAtMost(5)
    }

    @Test
    fun expectedScore_cappedAtExtremes() {
        assertThat(EloLite.expectedScorePermille(10_000)).isEqualTo(EloLite.MAX_EXPECTED_PERMILLE)
        assertThat(EloLite.expectedScorePermille(-10_000))
            .isEqualTo(EloLite.PERMILLE - EloLite.MAX_EXPECTED_PERMILLE)
    }

    @Test
    fun problemRating_isLinearInDifficulty() {
        assertThat(EloLite.problemRating(Difficulty.MIN)).isEqualTo(EloLite.PROBLEM_RATING_BASE)
        assertThat(EloLite.problemRating(Difficulty.MIN + 1))
            .isEqualTo(EloLite.PROBLEM_RATING_BASE + EloLite.RATING_PER_DIFFICULTY)
        assertThat(EloLite.problemRating(Difficulty.MAX))
            .isEqualTo(EloLite.PROBLEM_RATING_BASE + (Difficulty.MAX - Difficulty.MIN) * EloLite.RATING_PER_DIFFICULTY)
    }

    @Test
    fun problemRating_clampsOutOfRangeDifficulty() {
        assertThat(EloLite.problemRating(Difficulty.MIN - 5)).isEqualTo(EloLite.problemRating(Difficulty.MIN))
        assertThat(EloLite.problemRating(Difficulty.MAX + 5)).isEqualTo(EloLite.problemRating(Difficulty.MAX))
    }

    @Test
    fun kFactor_decaysAtScheduleBoundaries() {
        assertThat(EloLite.kFactor(0)).isEqualTo(EloLite.K_FACTOR_PLACEMENT)
        assertThat(EloLite.kFactor(EloLite.PLACEMENT_ATTEMPTS - 1)).isEqualTo(EloLite.K_FACTOR_PLACEMENT)
        assertThat(EloLite.kFactor(EloLite.PLACEMENT_ATTEMPTS)).isEqualTo(EloLite.K_FACTOR_DEVELOPING)
        assertThat(EloLite.kFactor(EloLite.DEVELOPING_ATTEMPTS - 1)).isEqualTo(EloLite.K_FACTOR_DEVELOPING)
        assertThat(EloLite.kFactor(EloLite.DEVELOPING_ATTEMPTS)).isEqualTo(EloLite.K_FACTOR_STABLE)
        assertThat(EloLite.kFactor(10_000)).isEqualTo(EloLite.K_FACTOR_STABLE)
    }

    @Test
    fun updatedRating_correctRaises_wrongLowers() {
        val rating = EloLite.INITIAL_ABILITY_RATING
        val evenOpponent = rating // 동급 문항 — 기대 500‰라 정답/오답 모두 반드시 움직인다.

        val afterCorrect = EloLite.updatedRating(rating, attemptsSoFar = 0, problemRating = evenOpponent, isCorrect = true)
        val afterWrong = EloLite.updatedRating(rating, attemptsSoFar = 0, problemRating = evenOpponent, isCorrect = false)

        assertThat(afterCorrect).isGreaterThan(rating)
        assertThat(afterWrong).isLessThan(rating)
    }

    @Test
    fun updatedRating_evenMatch_movesSymmetrically() {
        // 정수 나눗셈이 0 방향 절사라 정답 +Δ, 오답 −Δ의 크기가 같아야 한다.
        val rating = EloLite.INITIAL_ABILITY_RATING
        val gain = EloLite.updatedRating(rating, attemptsSoFar = 0, problemRating = rating, isCorrect = true) - rating
        val loss = rating - EloLite.updatedRating(rating, attemptsSoFar = 0, problemRating = rating, isCorrect = false)
        assertThat(gain).isEqualTo(loss)
    }

    @Test
    fun updatedRating_sameEvidence_movesLessWhenExperienced() {
        val rating = EloLite.INITIAL_ABILITY_RATING
        val opponent = rating

        val placementDelta =
            EloLite.updatedRating(rating, attemptsSoFar = 0, problemRating = opponent, isCorrect = true) - rating
        val stableDelta =
            EloLite.updatedRating(rating, attemptsSoFar = EloLite.DEVELOPING_ATTEMPTS, problemRating = opponent, isCorrect = true) - rating

        assertThat(placementDelta).isGreaterThan(stableDelta)
        assertThat(stableDelta).isGreaterThan(0)
    }

    @Test
    fun updatedRating_uninformativeExtremes_doNotMove() {
        val rating = EloLite.INITIAL_ABILITY_RATING
        val farBelow = rating - 1_000 // 아주 쉬운 문항
        val farAbove = rating + 1_000 // 아주 어려운 문항

        // 쉬운 문제 정답 = 정보 없음 → 갱신 0 (쉬운 문제 반복으로 θ 올리기 차단).
        val afterTrivialWin =
            EloLite.updatedRating(rating, attemptsSoFar = EloLite.DEVELOPING_ATTEMPTS, problemRating = farBelow, isCorrect = true)
        // 한참 위 문제 오답 = 정보 없음 → 갱신 0 (도전 실패가 θ를 깎지 않음).
        val afterHopelessLoss =
            EloLite.updatedRating(rating, attemptsSoFar = EloLite.DEVELOPING_ATTEMPTS, problemRating = farAbove, isCorrect = false)

        assertThat(afterTrivialWin).isEqualTo(rating)
        assertThat(afterHopelessLoss).isEqualTo(rating)
    }
}
