package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.common.toPercentInt
import com.ddakpul.math.domain.model.DayCell
import com.ddakpul.math.domain.model.Difficulty
import com.ddakpul.math.domain.model.LearningReport
import com.ddakpul.math.domain.model.LearningStats
import com.ddakpul.math.domain.model.MasteryCell
import com.ddakpul.math.domain.model.MathArea
import com.ddakpul.math.domain.model.ReportInsight
import com.ddakpul.math.domain.model.WeeklySummary
import javax.inject.Inject

/**
 * 집계된 [LearningStats]를 학부모가 읽을 수 있는 [LearningReport]로 해석한다 —
 * 어떤 인사이트를 띄우고 무엇을 "보강 필요"로 볼지는 교육 정책이므로 domain에 둔다.
 *
 * 순수 함수 — [today]는 호출부가 주입한다(로컬 자정 기준 epoch day).
 */
class BuildLearningReportUseCase
    @Inject
    constructor() {
        operator fun invoke(
            stats: LearningStats,
            dailyGoal: Int,
            today: Long,
        ): LearningReport =
            LearningReport(
                dayCells = buildDayCells(stats, today),
                insights = buildInsights(stats, dailyGoal),
                weeklySummary = buildWeeklySummary(stats, today),
                masteryGrid = buildMasteryGrid(stats),
            )

        /** 최근 [WINDOW_DAYS]일을 빈 날 포함해 채운다 — 차트의 x축이 끊기지 않게. */
        private fun buildDayCells(
            stats: LearningStats,
            today: Long,
        ): List<DayCell> {
            val byDay = stats.dailyStats.associateBy { it.epochDay }
            return ((today - WINDOW_DAYS + 1)..today).map { day ->
                val stat = byDay[day]
                DayCell(
                    epochDay = day,
                    solved = stat?.solved ?: 0,
                    accuracy = stat?.let { if (it.solved > 0) it.accuracy else null },
                    isToday = day == today,
                )
            }
        }

        /**
         * 영역×난이도 칸을 전부 채운다 — 시도 없는 칸도 solved=0으로 그리드에 나타나야 한다.
         * [LearningStats.matrixCells]는 시도가 있는 칸만 담으므로(집계 로직상 solved=0인 칸은
         * 만들어지지 않는다) `cell`이 있으면 항상 solved > 0이다.
         */
        private fun buildMasteryGrid(stats: LearningStats): List<MasteryCell> {
            val byKey = stats.matrixCells.associateBy { it.area to it.difficulty }
            return MathArea.entries.flatMap { area ->
                (Difficulty.MIN..Difficulty.MAX).map { difficulty ->
                    val cell = byKey[area to difficulty]
                    MasteryCell(
                        area = area,
                        difficulty = difficulty,
                        solved = cell?.solved ?: 0,
                        accuracy = cell?.accuracy,
                    )
                }
            }
        }

        // 목표 달성 판정은 홈·풀이 화면과 같은 '사용자가 고른 목표'를 쓴다 —
        // 상수 10을 쓰면 목표를 5로 낮춘 아이에게 리포트만 달성이라고 말하지 않는다(2026-08 QA).
        private fun buildInsights(
            stats: LearningStats,
            dailyGoal: Int,
        ): List<ReportInsight> =
            buildList {
                if (stats.todaySolved >= dailyGoal) add(ReportInsight.GoalDone)
                if (stats.streakDays >= MIN_STREAK_FOR_INSIGHT) add(ReportInsight.Streak(stats.streakDays))

                val recent = stats.recentAccuracy
                val previous = stats.previousAccuracy
                if (recent != null && previous != null) {
                    val delta = (recent - previous).toPercentInt()
                    when {
                        delta >= TREND_DELTA_THRESHOLD -> add(ReportInsight.AccuracyUp(delta))
                        delta <= -TREND_DELTA_THRESHOLD -> add(ReportInsight.AccuracyDown(-delta))
                    }
                }

                stats.errorRecoveryRate
                    ?.takeIf { it > 0f }
                    ?.let { add(ReportInsight.ErrorRecovery(it.toPercentInt())) }

                stats.weakestConcept()?.let { add(ReportInsight.WeakConcept(it.concept, it.accuracy.toPercentInt())) }
            }

        private fun buildWeeklySummary(
            stats: LearningStats,
            today: Long,
        ): WeeklySummary {
            val lastWeek = stats.dailyStats.filter { it.epochDay > today - DAYS_PER_WEEK }
            val solved = lastWeek.sumOf { it.solved }
            val correct = lastWeek.sumOf { it.correct }

            val recent = stats.recentAccuracy
            val previous = stats.previousAccuracy
            val delta =
                if (recent != null && previous != null) (recent - previous).toPercentInt() else null

            return WeeklySummary(
                solved = solved,
                studyDays = lastWeek.count { it.solved > 0 },
                accuracyPercent = if (solved > 0) (correct.toFloat() / solved).toPercentInt() else 0,
                deltaPercentPoint = delta,
                weakConcept = stats.weakestConcept()?.concept,
            )
        }

        /**
         * 보강을 권할 개념 — 충분히 풀어봤는데도 정답률이 낮은 것 중 가장 낮은 하나.
         * 인사이트와 주간 요약이 같은 기준을 써야 두 곳의 말이 어긋나지 않는다.
         * ([LearningStats.conceptStats]는 정답률 오름차순이다.)
         */
        private fun LearningStats.weakestConcept() = conceptStats.firstOrNull { it.solved >= MIN_SOLVED_FOR_CONCEPT && it.accuracy < WEAK_ACCURACY }

        private companion object {
            const val WINDOW_DAYS = 14L
            const val DAYS_PER_WEEK = 7L

            /** 인사이트로 띄울 최소 연속 학습일. */
            const val MIN_STREAK_FOR_INSIGHT = 2

            /** 정답률 추이 인사이트를 띄우는 최소 변화폭(%p). */
            const val TREND_DELTA_THRESHOLD = 5

            /** 개념 인사이트를 띄우려면 최소 이만큼은 풀어봤어야 한다. */
            const val MIN_SOLVED_FOR_CONCEPT = 3

            /** 이 정답률 미만이면 "보강 필요" 개념. */
            const val WEAK_ACCURACY = 0.6f
        }
    }
