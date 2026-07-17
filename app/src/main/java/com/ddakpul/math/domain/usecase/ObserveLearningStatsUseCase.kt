package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.model.AreaStat
import com.ddakpul.math.domain.model.Attempt
import com.ddakpul.math.domain.model.ConceptStat
import com.ddakpul.math.domain.model.DailyStat
import com.ddakpul.math.domain.model.DifficultyPoint
import com.ddakpul.math.domain.model.LearningStats
import com.ddakpul.math.domain.model.MathArea
import com.ddakpul.math.domain.model.MatrixCell
import com.ddakpul.math.domain.model.Problem
import com.ddakpul.math.domain.repository.LearnerRepository
import com.ddakpul.math.domain.repository.ProblemRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.emitAll
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import kotlin.math.roundToInt

/**
 * 학습 기록을 [LearningStats]로 집계해 스트림으로 노출한다.
 * 시간(현재 시각·타임존 오프셋)은 호출부(ViewModel)가 주입해 domain을 순수하게 유지한다.
 */
class ObserveLearningStatsUseCase
    @Inject
    constructor(
        private val learnerRepository: LearnerRepository,
        private val problemRepository: ProblemRepository,
    ) {
        operator fun invoke(
            zoneOffsetMillis: Long,
            nowMillis: () -> Long,
        ): Flow<LearningStats> =
            flow {
                val problemsById =
                    problemRepository.getAllGroups().flatMap { it.problems }.associateBy { it.id }
                emitAll(
                    learnerRepository.observeAttempts().map { attempts ->
                        buildLearningStats(
                            attempts = attempts,
                            problemsById = problemsById,
                            currentDifficulty = learnerRepository.getCurrentDifficulty(),
                            zoneOffsetMillis = zoneOffsetMillis,
                            nowMillis = nowMillis(),
                        )
                    },
                )
            }
    }

/** 정답률 추이 비교 구간(최근 N일 vs 그 전 N일). */
internal const val TREND_WINDOW_DAYS = 7

/** 오답 노트에 보여줄 최대 문제 수. */
internal const val RECENT_MISTAKES_LIMIT = 6

/** 순수 집계 로직 — 단위 테스트로 검증한다. [attempts]는 시간 오름차순. */
internal fun buildLearningStats(
    attempts: List<Attempt>,
    problemsById: Map<String, Problem>,
    currentDifficulty: Int,
    zoneOffsetMillis: Long,
    nowMillis: Long,
): LearningStats {
    @Suppress("NAME_SHADOWING")
    val attempts = normalizeAttempts(attempts, problemsById)
    val today = epochDay(nowMillis, zoneOffsetMillis)

    val areaStats =
        MathArea.entries.map { area ->
            val inArea = attempts.filter { problemsById[it.problemId]?.area == area }
            AreaStat(area = area, solved = inArea.size, correct = inArea.count { it.isCorrect })
        }

    val dailyStats =
        attempts
            .groupBy { epochDay(it.timestamp, zoneOffsetMillis) }
            .map { (day, inDay) ->
                DailyStat(
                    epochDay = day,
                    solved = inDay.size,
                    correct = inDay.count { it.isCorrect },
                    timeSpentSec = inDay.sumOf { it.timeSpentSec },
                )
            }.sortedBy { it.epochDay }

    val conceptStats =
        attempts
            .flatMap { attempt ->
                val problem = problemsById[attempt.problemId] ?: return@flatMap emptyList()
                problem.conceptTags.map { tag -> Triple(tag, problem.area, attempt.isCorrect) }
            }.groupBy({ it.first to it.second }, { it.third })
            .map { (key, results) ->
                ConceptStat(
                    concept = key.first,
                    area = key.second,
                    solved = results.size,
                    correct = results.count { it },
                )
            }.sortedBy { it.accuracy }

    val difficultyProgress =
        attempts.mapNotNull { attempt ->
            problemsById[attempt.problemId]?.let { DifficultyPoint(attempt.timestamp, it.difficulty) }
        }

    val matrixCells =
        attempts
            .mapNotNull { attempt -> problemsById[attempt.problemId]?.let { it to attempt } }
            .groupBy({ (problem, _) -> problem.area to problem.difficulty }, { (_, attempt) -> attempt })
            .map { (key, inCell) ->
                MatrixCell(
                    area = key.first,
                    difficulty = key.second,
                    solved = inCell.size,
                    correct = inCell.count { it.isCorrect },
                )
            }

    val studyDays = dailyStats.mapTo(sortedSetOf()) { it.epochDay }
    val (streak, bestStreak) = computeStreaks(studyDays, today)

    val todayAttempts = attempts.filter { epochDay(it.timestamp, zoneOffsetMillis) == today }

    val avgTimeSecByDifficulty =
        attempts
            .mapNotNull { attempt ->
                problemsById[attempt.problemId]?.let { it.difficulty to attempt.timeSpentSec }
            }.groupBy({ it.first }, { it.second })
            .mapValues { (_, times) -> times.average().roundToInt() }

    val recentCutoff = nowMillis - TREND_WINDOW_DAYS * MILLIS_PER_DAY
    val previousCutoff = nowMillis - 2L * TREND_WINDOW_DAYS * MILLIS_PER_DAY
    val recent = attempts.filter { it.timestamp >= recentCutoff }
    val previous = attempts.filter { it.timestamp in previousCutoff until recentCutoff }

    val errorRecoveryRate = computeErrorRecoveryRate(attempts)

    // 오답 노트 — 각 문제의 '가장 최근 시도'가 오답인 문제들을 최신순으로. (attempts는 시간 오름차순)
    val recentMistakes =
        attempts
            .groupBy { it.problemId }
            .mapNotNull { (id, tries) ->
                val last = tries.last()
                if (!last.isCorrect) problemsById[id]?.let { it to last.timestamp } else null
            }.sortedByDescending { it.second }
            .take(RECENT_MISTAKES_LIMIT)
            .map { it.first }

    return LearningStats(
        totalSolved = attempts.size,
        correctCount = attempts.count { it.isCorrect },
        currentDifficulty = currentDifficulty,
        areaStats = areaStats,
        dailyStats = dailyStats,
        conceptStats = conceptStats,
        difficultyProgress = difficultyProgress,
        matrixCells = matrixCells,
        streakDays = streak,
        bestStreakDays = bestStreak,
        todaySolved = todayAttempts.size,
        todayCorrect = todayAttempts.count { it.isCorrect },
        todayTimeSpentSec = todayAttempts.sumOf { it.timeSpentSec },
        avgTimeSecByDifficulty = avgTimeSecByDifficulty,
        recentAccuracy = recent.accuracyOrNull(),
        previousAccuracy = previous.accuracyOrNull(),
        errorRecoveryRate = errorRecoveryRate,
        recentMistakes = recentMistakes,
    )
}

/**
 * 일관성 불변식: 모든 통계는 '현재 문제은행에 있는 문제'의 시도만 센다 —
 * 은행에서 제거된 문제(blocklist 등)의 옛 시도가 전체 합계에만 남으면 표끼리 합이 안 맞는다.
 * 시간은 기록 상한으로 clamp — 상한 도입 전 기록된 이상치(밤새 열어둔 문제) 방어.
 */
private fun normalizeAttempts(
    attempts: List<Attempt>,
    problemsById: Map<String, Problem>,
): List<Attempt> =
    attempts
        .filter { it.problemId in problemsById }
        .map { attempt ->
            if (attempt.timeSpentSec > Attempt.MAX_TIME_SPENT_SEC) {
                attempt.copy(timeSpentSec = Attempt.MAX_TIME_SPENT_SEC)
            } else {
                attempt
            }
        }

/** 한 번이라도 틀린 문제 중, 첫 오답 이후 다시 풀어 맞힌 문제의 비율. [attempts]는 시간 오름차순. */
private fun computeErrorRecoveryRate(attempts: List<Attempt>): Float? {
    val byProblem = attempts.groupBy { it.problemId }
    val everWrong = byProblem.filterValues { tries -> tries.any { !it.isCorrect } }
    if (everWrong.isEmpty()) return null
    val recovered =
        everWrong.values.count { tries ->
            val firstWrongIndex = tries.indexOfFirst { !it.isCorrect }
            tries.drop(firstWrongIndex + 1).any { it.isCorrect }
        }
    return recovered.toFloat() / everWrong.size
}

private fun List<Attempt>.accuracyOrNull(): Float? = if (isEmpty()) null else count { it.isCorrect }.toFloat() / size

/**
 * @return (현재 스트릭, 최고 스트릭). 현재 스트릭은 오늘 또는 어제로 끝나는 연속 구간의 길이 —
 * 어제까지 이어졌다면 아직 깨진 게 아니다(오늘 풀면 이어진다).
 */
private fun computeStreaks(
    studyDays: Collection<Long>,
    today: Long,
): Pair<Int, Int> {
    if (studyDays.isEmpty()) return 0 to 0
    val days = studyDays.toSortedSet()

    var bestStreak = 1
    var run = 1
    var prev: Long? = null
    for (day in days) {
        run = if (prev != null && day == prev + 1) run + 1 else 1
        if (run > bestStreak) bestStreak = run
        prev = day
    }

    val anchor =
        when {
            today in days -> today
            (today - 1) in days -> today - 1
            else -> return 0 to bestStreak
        }
    var streak = 0
    var cursor = anchor
    while (cursor in days) {
        streak++
        cursor--
    }
    return streak to bestStreak
}
