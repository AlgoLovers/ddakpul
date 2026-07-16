package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.model.AreaStat
import com.ddakpul.math.domain.model.LearningStats
import com.ddakpul.math.domain.model.MathArea
import com.ddakpul.math.domain.model.NextStep
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class ComputeNextStepUseCaseTest {
    private val useCase = ComputeNextStepUseCase()

    private fun stats(
        todaySolved: Int = 5,
        streakDays: Int = 0,
        areaStats: List<AreaStat> = emptyList(),
        recentAccuracy: Float? = null,
    ) = LearningStats(
        totalSolved = 50,
        correctCount = 30,
        currentDifficulty = 3,
        areaStats = areaStats,
        dailyStats = emptyList(),
        conceptStats = emptyList(),
        difficultyProgress = emptyList(),
        matrixCells = emptyList(),
        streakDays = streakDays,
        bestStreakDays = streakDays,
        todaySolved = todaySolved,
        todayCorrect = todaySolved,
        todayTimeSpentSec = 300,
        avgTimeSecByDifficulty = emptyMap(),
        recentAccuracy = recentAccuracy,
        previousAccuracy = null,
        errorRecoveryRate = null,
    )

    @Test
    fun `오늘 안 풀었으면 StartToday`() {
        assertEquals(NextStep.StartToday, useCase(stats(todaySolved = 0)))
    }

    @Test
    fun `뚜렷이 약한 영역이 있으면 FocusArea`() {
        val weak = AreaStat(MathArea.SHAPE_MEASUREMENT, solved = 10, correct = 3) // 30%
        val step = useCase(stats(todaySolved = 5, areaStats = listOf(weak)))
        assertTrue(step is NextStep.FocusArea && step.area == MathArea.SHAPE_MEASUREMENT)
    }

    @Test
    fun `표본이 적은 영역은 취약으로 단정하지 않는다`() {
        val few = AreaStat(MathArea.SHAPE_MEASUREMENT, solved = 2, correct = 0) // 0%지만 2문제뿐
        val step = useCase(stats(todaySolved = 5, areaStats = listOf(few), streakDays = 3))
        assertTrue(step is NextStep.KeepStreak) // FocusArea 아님 → 다음 규칙(연속)으로
    }

    @Test
    fun `최근 정답률이 높으면 ReadyForHarder`() {
        assertEquals(NextStep.ReadyForHarder, useCase(stats(todaySolved = 5, recentAccuracy = 0.9f)))
    }

    @Test
    fun `연속 학습 중이면 KeepStreak`() {
        val step = useCase(stats(todaySolved = 5, streakDays = 4))
        assertTrue(step is NextStep.KeepStreak && step.days == 4)
    }

    @Test
    fun `특별한 신호가 없으면 Encourage`() {
        assertEquals(NextStep.Encourage, useCase(stats(todaySolved = 5)))
    }

    @Test
    fun `취약 영역이 연속보다 우선한다`() {
        val weak = AreaStat(MathArea.NUMBER_OPERATION, solved = 8, correct = 2) // 25%
        val step = useCase(stats(todaySolved = 5, areaStats = listOf(weak), streakDays = 5))
        assertTrue(step is NextStep.FocusArea)
    }
}
