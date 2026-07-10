package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.model.MathArea
import com.ddakpul.math.domain.usecase.TestFixtures.attempt
import com.ddakpul.math.domain.usecase.TestFixtures.problem
import com.google.common.truth.Truth.assertThat
import org.junit.Test

class BuildLearningStatsTest {
    private val problems =
        listOf(
            problem("num1", difficulty = 2, area = MathArea.NUMBER_OPERATION, concepts = listOf("분수의 덧셈")),
            problem("num2", difficulty = 3, area = MathArea.NUMBER_OPERATION, concepts = listOf("분수의 덧셈", "소수")),
            problem("geo1", difficulty = 2, area = MathArea.SHAPE_MEASUREMENT, concepts = listOf("각도")),
        )
    private val problemsById = problems.associateBy { it.id }

    private fun build(
        attempts: List<com.ddakpul.math.domain.model.Attempt>,
        nowMillis: Long = DAY * 100,
        zoneOffsetMillis: Long = 0L,
        currentDifficulty: Int = 3,
    ) = buildLearningStats(attempts, problemsById, currentDifficulty, zoneOffsetMillis, nowMillis)

    @Test
    fun aggregatesTotalsAndAreaStats() {
        val stats =
            build(
                listOf(
                    attempt("num1", true, timestamp = DAY * 100),
                    attempt("num2", false, timestamp = DAY * 100),
                    attempt("geo1", true, timestamp = DAY * 100),
                ),
            )

        assertThat(stats.totalSolved).isEqualTo(3)
        assertThat(stats.correctCount).isEqualTo(2)
        assertThat(stats.accuracy).isWithin(TOLERANCE).of(2f / 3f)
        val numberStat = stats.areaStats.first { it.area == MathArea.NUMBER_OPERATION }
        assertThat(numberStat.solved).isEqualTo(2)
        assertThat(numberStat.correct).isEqualTo(1)
        // 시도가 없는 영역도 0/0으로 존재한다.
        assertThat(stats.areaStats.first { it.area == MathArea.DATA_POSSIBILITY }.solved).isEqualTo(0)
    }

    @Test
    fun dailyStats_groupByLocalDay_respectingZoneOffset() {
        // UTC 기준 23:30과 다음날 00:30 — 오프셋 +1h를 주면 같은 날(자정 넘김)로 묶이지 않고
        // 23:30+1h=다음날 00:30, 00:30+1h=다음날 01:30으로 둘 다 "다음날"이 된다.
        val lateNight = DAY * 10 - 30 * MINUTE
        val earlyMorning = DAY * 10 + 30 * MINUTE
        val stats =
            build(
                listOf(
                    attempt("num1", true, timestamp = lateNight),
                    attempt("num2", true, timestamp = earlyMorning),
                ),
                zoneOffsetMillis = HOUR,
            )

        assertThat(stats.dailyStats).hasSize(1)
        assertThat(stats.dailyStats.first().epochDay).isEqualTo(10)
        assertThat(stats.dailyStats.first().solved).isEqualTo(2)
    }

    @Test
    fun streak_countsConsecutiveDaysEndingToday() {
        val now = DAY * 100 + HOUR
        val stats =
            build(
                listOf(
                    attempt("num1", true, timestamp = DAY * 98),
                    attempt("num1", true, timestamp = DAY * 99),
                    attempt("num1", true, timestamp = DAY * 100),
                ),
                nowMillis = now,
            )

        assertThat(stats.streakDays).isEqualTo(3)
        assertThat(stats.bestStreakDays).isEqualTo(3)
    }

    @Test
    fun streak_aliveWhenLastStudyWasYesterday() {
        val now = DAY * 100 + HOUR
        val stats =
            build(
                listOf(
                    attempt("num1", true, timestamp = DAY * 98),
                    attempt("num1", true, timestamp = DAY * 99),
                ),
                nowMillis = now,
            )

        // 어제까지 이틀 연속 — 오늘 아직 안 풀었어도 스트릭은 살아 있다.
        assertThat(stats.streakDays).isEqualTo(2)
    }

    @Test
    fun streak_zeroAfterOneFullDayGap_butBestStreakRemembered() {
        val now = DAY * 100 + HOUR
        val stats =
            build(
                listOf(
                    attempt("num1", true, timestamp = DAY * 95),
                    attempt("num1", true, timestamp = DAY * 96),
                    attempt("num1", true, timestamp = DAY * 97),
                ),
                nowMillis = now,
            )

        assertThat(stats.streakDays).isEqualTo(0)
        assertThat(stats.bestStreakDays).isEqualTo(3)
    }

    @Test
    fun todayCounts_onlyIncludeTodayAttempts() {
        val now = DAY * 100 + 2 * HOUR
        val stats =
            build(
                listOf(
                    attempt("num1", true, timestamp = DAY * 99, timeSpentSec = 100),
                    attempt("num2", false, timestamp = DAY * 100 + HOUR, timeSpentSec = 30),
                    attempt("geo1", true, timestamp = DAY * 100 + HOUR, timeSpentSec = 45),
                ),
                nowMillis = now,
            )

        assertThat(stats.todaySolved).isEqualTo(2)
        assertThat(stats.todayCorrect).isEqualTo(1)
        // 어제 쓴 100초는 빠지고 오늘 것만 합산된다.
        assertThat(stats.todayTimeSpentSec).isEqualTo(75)
    }

    @Test
    fun avgTimeByDifficulty_averagesAndRounds() {
        val stats =
            build(
                listOf(
                    // 난이도 2: num1(10초), geo1(15초) → 평균 12.5 → 13
                    attempt("num1", true, timestamp = DAY * 100, timeSpentSec = 10),
                    attempt("geo1", true, timestamp = DAY * 100, timeSpentSec = 15),
                    // 난이도 3: num2(30초)
                    attempt("num2", false, timestamp = DAY * 100, timeSpentSec = 30),
                ),
            )

        assertThat(stats.avgTimeSecByDifficulty).containsEntry(2, 13)
        assertThat(stats.avgTimeSecByDifficulty).containsEntry(3, 30)
    }

    @Test
    fun accuracyTrend_splitsRecentAndPreviousWindows() {
        val now = DAY * 100
        val stats =
            build(
                listOf(
                    // 이전 7일 구간(8~14일 전): 1/2 정답
                    attempt("num1", true, timestamp = now - 10 * DAY),
                    attempt("num1", false, timestamp = now - 9 * DAY),
                    // 최근 7일 구간: 2/2 정답
                    attempt("num1", true, timestamp = now - 2 * DAY),
                    attempt("num1", true, timestamp = now - DAY),
                ),
                nowMillis = now,
            )

        assertThat(stats.recentAccuracy).isWithin(TOLERANCE).of(1f)
        assertThat(stats.previousAccuracy).isWithin(TOLERANCE).of(0.5f)
    }

    @Test
    fun errorRecoveryRate_countsWrongProblemsLaterSolved() {
        val stats =
            build(
                listOf(
                    // num1: 틀림 → 다시 맞힘 (해소)
                    attempt("num1", false, timestamp = DAY * 99),
                    attempt("num1", true, timestamp = DAY * 100),
                    // num2: 틀리고 재도전 없음 (미해소)
                    attempt("num2", false, timestamp = DAY * 100),
                ),
            )

        assertThat(stats.errorRecoveryRate).isWithin(TOLERANCE).of(0.5f)
    }

    @Test
    fun errorRecoveryRate_nullWhenNoWrongAttempts() {
        val stats = build(listOf(attempt("num1", true, timestamp = DAY * 100)))

        assertThat(stats.errorRecoveryRate).isNull()
    }

    @Test
    fun difficultyProgress_mapsAttemptsToProblemDifficulty_skippingUnknown() {
        val stats =
            build(
                listOf(
                    attempt("num1", true, timestamp = DAY * 99),
                    attempt("ghost", true, timestamp = DAY * 99 + HOUR),
                    attempt("num2", false, timestamp = DAY * 100),
                ),
            )

        assertThat(stats.difficultyProgress.map { it.difficulty }).containsExactly(2, 3).inOrder()
    }

    @Test
    fun conceptStats_aggregatePerTag_sortedByAccuracyAscending() {
        val stats =
            build(
                listOf(
                    // "분수의 덧셈": num1(정답) + num2(오답) = 1/2
                    // "소수": num2(오답) = 0/1
                    // "각도": geo1(정답) = 1/1
                    attempt("num1", true, timestamp = DAY * 100),
                    attempt("num2", false, timestamp = DAY * 100),
                    attempt("geo1", true, timestamp = DAY * 100),
                ),
            )

        val byConcept = stats.conceptStats.associateBy { it.concept }
        assertThat(byConcept["분수의 덧셈"]?.solved).isEqualTo(2)
        assertThat(byConcept["분수의 덧셈"]?.correct).isEqualTo(1)
        assertThat(byConcept["소수"]?.accuracy).isEqualTo(0f)
        assertThat(byConcept["각도"]?.accuracy).isEqualTo(1f)
        // 취약(정답률 낮은) 순 정렬
        assertThat(stats.conceptStats.first().concept).isEqualTo("소수")
        assertThat(stats.conceptStats.last().concept).isEqualTo("각도")
    }

    @Test
    fun emptyAttempts_yieldEmptyStats() {
        val stats = build(emptyList())

        assertThat(stats.isEmpty).isTrue()
        assertThat(stats.streakDays).isEqualTo(0)
        assertThat(stats.recentAccuracy).isNull()
        assertThat(stats.errorRecoveryRate).isNull()
    }

    private companion object {
        const val TOLERANCE = 0.0001f
        const val MINUTE = 60_000L
        const val HOUR = 3_600_000L
        const val DAY = 86_400_000L
    }
}
