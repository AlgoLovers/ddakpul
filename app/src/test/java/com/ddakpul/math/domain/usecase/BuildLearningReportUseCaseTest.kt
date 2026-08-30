package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.model.ConceptStat
import com.ddakpul.math.domain.model.DailyStat
import com.ddakpul.math.domain.model.Difficulty
import com.ddakpul.math.domain.model.LearningStats
import com.ddakpul.math.domain.model.MathArea
import com.ddakpul.math.domain.model.MatrixCell
import com.ddakpul.math.domain.model.ReportInsight
import com.google.common.truth.Truth.assertThat
import org.junit.Test

/**
 * 리포트 해석 규칙(어떤 인사이트를 언제 띄우는지, 취약 개념 기준)의 고정.
 * 이 계산은 ViewModel 안에 있어 테스트가 불가능했다 — domain으로 옮기면서 규칙을 못 박는다.
 */
class BuildLearningReportUseCaseTest {
    private val buildReport = BuildLearningReportUseCase()

    private fun stats(
        dailyStats: List<DailyStat> = emptyList(),
        conceptStats: List<ConceptStat> = emptyList(),
        matrixCells: List<MatrixCell> = emptyList(),
        streakDays: Int = 0,
        todaySolved: Int = 0,
        recentAccuracy: Float? = null,
        previousAccuracy: Float? = null,
        errorRecoveryRate: Float? = null,
    ) = LearningStats(
        totalSolved = dailyStats.sumOf { it.solved },
        correctCount = dailyStats.sumOf { it.correct },
        currentDifficulty = Difficulty.DEFAULT,
        areaStats = emptyList(),
        dailyStats = dailyStats,
        conceptStats = conceptStats,
        difficultyProgress = emptyList(),
        matrixCells = matrixCells,
        streakDays = streakDays,
        bestStreakDays = streakDays,
        todaySolved = todaySolved,
        todayCorrect = todaySolved,
        todayTimeSpentSec = 0,
        avgTimeSecByDifficulty = emptyMap(),
        recentAccuracy = recentAccuracy,
        previousAccuracy = previousAccuracy,
        errorRecoveryRate = errorRecoveryRate,
    )

    @Test
    fun `최근 14일을 빈 날까지 채워 차트 축이 끊기지 않는다`() {
        val report =
            buildReport(
                stats = stats(dailyStats = listOf(DailyStat(epochDay = TODAY, solved = 3, correct = 2, timeSpentSec = 60))),
                dailyGoal = 10,
                today = TODAY,
            )

        assertThat(report.dayCells).hasSize(14)
        assertThat(report.dayCells.last().epochDay).isEqualTo(TODAY)
        assertThat(report.dayCells.last().isToday).isTrue()
        assertThat(report.dayCells.first().solved).isEqualTo(0)
        // 학습이 없던 날은 정답률이 0%가 아니라 '없음' — 0으로 그리면 추이가 폭락한 것처럼 보인다.
        assertThat(report.dayCells.first().accuracy).isNull()
    }

    @Test
    fun `숙달 지도는 시도 없는 칸까지 전부 채운다`() {
        val report =
            buildReport(
                stats = stats(matrixCells = listOf(MatrixCell(MathArea.NUMBER_OPERATION, Difficulty.MIN, solved = 2, correct = 2))),
                dailyGoal = 10,
                today = TODAY,
            )

        val expectedCells = MathArea.entries.size * (Difficulty.MAX - Difficulty.MIN + 1)
        assertThat(report.masteryGrid).hasSize(expectedCells)
        assertThat(report.masteryGrid.count { it.solved == 0 }).isEqualTo(expectedCells - 1)
    }

    @Test
    fun `목표 달성은 상수가 아니라 아이가 고른 목표로 판정한다`() {
        val fiveSolved = stats(todaySolved = 5)

        assertThat(buildReport(fiveSolved, dailyGoal = 5, today = TODAY).insights).contains(ReportInsight.GoalDone)
        assertThat(buildReport(fiveSolved, dailyGoal = 10, today = TODAY).insights).doesNotContain(ReportInsight.GoalDone)
    }

    @Test
    fun `정답률 변화가 기준폭을 넘어야 추이 인사이트가 뜬다`() {
        val small = buildReport(stats(recentAccuracy = 0.72f, previousAccuracy = 0.70f), dailyGoal = 10, today = TODAY)
        assertThat(small.insights.filterIsInstance<ReportInsight.AccuracyUp>()).isEmpty()

        val big = buildReport(stats(recentAccuracy = 0.85f, previousAccuracy = 0.70f), dailyGoal = 10, today = TODAY)
        assertThat(big.insights).contains(ReportInsight.AccuracyUp(15))

        val down = buildReport(stats(recentAccuracy = 0.50f, previousAccuracy = 0.70f), dailyGoal = 10, today = TODAY)
        assertThat(down.insights).contains(ReportInsight.AccuracyDown(20))
    }

    @Test
    fun `표본이 적은 개념은 취약으로 낙인찍지 않는다`() {
        val tooFew = ConceptStat(concept = "규칙 찾기", area = MathArea.NUMBER_OPERATION, solved = 2, correct = 0)
        val report = buildReport(stats(conceptStats = listOf(tooFew)), dailyGoal = 10, today = TODAY)

        assertThat(report.insights.filterIsInstance<ReportInsight.WeakConcept>()).isEmpty()
        assertThat(report.weeklySummary?.weakConcept).isNull()
    }

    @Test
    fun `취약 개념은 인사이트와 주간 요약이 같은 것을 가리킨다`() {
        val weak = ConceptStat(concept = "규칙 찾기", area = MathArea.NUMBER_OPERATION, solved = 5, correct = 2)
        val fine = ConceptStat(concept = "도형 세기", area = MathArea.SHAPE_MEASUREMENT, solved = 5, correct = 5)
        val report = buildReport(stats(conceptStats = listOf(weak, fine)), dailyGoal = 10, today = TODAY)

        assertThat(report.insights).contains(ReportInsight.WeakConcept("규칙 찾기", 40))
        assertThat(report.weeklySummary?.weakConcept).isEqualTo("규칙 찾기")
    }

    @Test
    fun `주간 요약은 최근 7일만 집계한다`() {
        val report =
            buildReport(
                stats =
                    stats(
                        dailyStats =
                            listOf(
                                DailyStat(epochDay = TODAY - 10, solved = 100, correct = 100, timeSpentSec = 0),
                                DailyStat(epochDay = TODAY - 2, solved = 4, correct = 3, timeSpentSec = 0),
                                DailyStat(epochDay = TODAY, solved = 6, correct = 3, timeSpentSec = 0),
                            ),
                    ),
                dailyGoal = 10,
                today = TODAY,
            )

        val summary = requireNotNull(report.weeklySummary)
        assertThat(summary.solved).isEqualTo(10)
        assertThat(summary.studyDays).isEqualTo(2)
        assertThat(summary.accuracyPercent).isEqualTo(60)
    }

    @Test
    fun `오답 해소율이 0이면 인사이트로 띄우지 않는다`() {
        assertThat(buildReport(stats(errorRecoveryRate = 0f), dailyGoal = 10, today = TODAY).insights)
            .doesNotContain(ReportInsight.ErrorRecovery(0))
        assertThat(buildReport(stats(errorRecoveryRate = 0.5f), dailyGoal = 10, today = TODAY).insights)
            .contains(ReportInsight.ErrorRecovery(50))
    }

    private companion object {
        /** 2026-01-01 기준 epoch day — 특정 날짜에 의존하지 않되 0 경계 효과는 피한다. */
        const val TODAY = 20_454L
    }
}
