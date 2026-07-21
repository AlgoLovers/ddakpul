package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.model.Difficulty
import com.google.common.truth.Truth.assertThat
import org.junit.Test
import kotlin.math.abs

/** 85% 규칙 선택 밴드(SuggestTargetDifficulty)의 성질을 고정한다. */
class SuggestTargetDifficultyTest {
    @Test
    fun freshLearner_targetsDefaultDifficulty() {
        // 초기 θ는 정의상 기대정답률 85% 조준점이 Difficulty.DEFAULT가 되도록 놓여 있다.
        val band = suggestTargetDifficulty(EloLite.INITIAL_ABILITY_RATING)

        assertThat(band.targetDifficulty).isEqualTo(Difficulty.DEFAULT)
    }

    @Test
    fun thetaAtEachRung_targetsThatRung() {
        // θ = b(난이도) + 목표 레이팅차 → 그 난이도가 정확히 85% 조준점.
        (Difficulty.MIN..Difficulty.MAX).forEach { difficulty ->
            val theta = EloLite.problemRating(difficulty) + EloLite.TARGET_RATING_GAP

            assertThat(suggestTargetDifficulty(theta).targetDifficulty).isEqualTo(difficulty)
        }
    }

    @Test
    fun targetNeverDecreasesAsThetaGrows() {
        var previousTarget = Difficulty.MIN
        (0..4_000 step 10).forEach { theta ->
            val target = suggestTargetDifficulty(theta).targetDifficulty

            assertThat(target).isAtLeast(previousTarget)
            previousTarget = target
        }
    }

    @Test
    fun extremelyLowTheta_clampsToMinDifficulty() {
        val band = suggestTargetDifficulty(0)

        assertThat(band.targetDifficulty).isEqualTo(Difficulty.MIN)
        assertThat(band.minDifficulty).isEqualTo(Difficulty.MIN)
        assertThat(band.maxDifficulty).isEqualTo(Difficulty.MIN)
    }

    @Test
    fun extremelyHighTheta_clampsToMaxDifficulty() {
        val band = suggestTargetDifficulty(10_000)

        assertThat(band.targetDifficulty).isEqualTo(Difficulty.MAX)
        assertThat(band.minDifficulty).isEqualTo(Difficulty.MAX)
        assertThat(band.maxDifficulty).isEqualTo(Difficulty.MAX)
    }

    @Test
    fun band_alwaysContainsTargetAndStaysInDifficultyRange() {
        (0..4_000 step 37).forEach { theta ->
            val band = suggestTargetDifficulty(theta)

            assertThat(band.minDifficulty).isAtMost(band.targetDifficulty)
            assertThat(band.maxDifficulty).isAtLeast(band.targetDifficulty)
            assertThat(band.minDifficulty).isAtLeast(Difficulty.MIN)
            assertThat(band.maxDifficulty).isAtMost(Difficulty.MAX)
        }
    }

    @Test
    fun bandMembers_haveExpectedSuccessWithinTolerance() {
        // 두 난이도 사이(rung 사이)의 θ — 밴드에 든 난이도는 전부 목표 ± 허용 오차 안이어야 한다.
        val theta = 2_000
        val band = suggestTargetDifficulty(theta)

        (band.minDifficulty..band.maxDifficulty).forEach { difficulty ->
            val expected = EloLite.expectedScorePermille(theta - EloLite.problemRating(difficulty))

            assertThat(abs(expected - EloLite.TARGET_SUCCESS_PERMILLE))
                .isAtMost(EloLite.TARGET_BAND_TOLERANCE_PERMILLE)
        }
    }
}
