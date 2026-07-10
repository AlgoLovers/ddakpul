package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.model.Attempt
import com.ddakpul.math.domain.model.Difficulty
import com.ddakpul.math.domain.model.LearnerState
import com.ddakpul.math.domain.model.Problem
import com.ddakpul.math.domain.model.ProblemGroup
import com.ddakpul.math.domain.model.Recommendation
import com.ddakpul.math.domain.model.RecommendationReason
import javax.inject.Inject
import kotlin.math.abs
import kotlin.random.Random

/** 추천 알고리즘 상수 — CLAUDE.md 추천 규칙 1·2·4와 1:1 대응. 매직값 금지. */
object RecommendationRules {
    /** 규칙1: 이만큼 연속으로 맞히면 난이도 +1. */
    const val PROMOTE_STREAK = 2

    /** 규칙2: 이만큼 연속으로 틀리면 난이도 −1. */
    const val DEMOTE_STREAK = 2

    /** 규칙4: 같은 난이도에서 누적 오답이 이 값 이상이면 "정체"로 보고 해설 + 선수 개념 복귀. */
    const val STAGNATION_WRONG = 3
}

/**
 * 다음에 낼 문제를 순수 규칙으로 결정한다(런타임 AI 호출 0원, 온디바이스 완결).
 *
 * 규칙(우선순위 순):
 * 1. 기록 없음 → 현재 난이도에서 시작([RecommendationReason.START]).
 * 2. 규칙4(정체): 현재 난이도에서 누적 오답 ≥ [RecommendationRules.STAGNATION_WRONG]
 *    → 난이도 −1 + 대표문제 해설 제공([RecommendationReason.REMEDIATION]). 안전망이라 가장 먼저 본다.
 * 3. 규칙1(상승): 최근 연속 정답 ≥ [RecommendationRules.PROMOTE_STREAK] → 난이도 +1.
 * 4. 규칙2(하강): 최근 연속 오답 ≥ [RecommendationRules.DEMOTE_STREAK] → 난이도 −1.
 * 5. 규칙3(혼조): 그 외 → 같은 난이도 유지.
 *
 * 결정된 난이도의 그룹을 고르고(규칙6: 없으면 가장 가까운 난이도로 폴백), 그 안에서
 * 최근에 풀지 않은 문제를 랜덤으로 낸다(규칙5). [random]을 주입해 테스트에서 결정적으로 만든다.
 */
class RecommendNextProblemUseCase
    @Inject
    constructor() {
        operator fun invoke(
            state: LearnerState,
            groups: List<ProblemGroup>,
            random: Random = Random.Default,
        ): Recommendation? {
            if (groups.isEmpty()) return null
            val problemsById = groups.flatMap { it.problems }.associateBy { it.id }
            val decision = decideDifficulty(state, problemsById)
            val group = selectGroup(groups, decision.difficulty, random) ?: return null
            val problem = selectProblem(group, state.recentAttempts, random) ?: return null
            return Recommendation(
                problem = problem,
                group = group,
                targetDifficulty = decision.difficulty,
                reason = decision.reason,
                showExplanation = decision.reason == RecommendationReason.REMEDIATION,
            )
        }

        private data class Decision(
            val difficulty: Int,
            val reason: RecommendationReason,
        )

        private fun decideDifficulty(
            state: LearnerState,
            problemsById: Map<String, Problem>,
        ): Decision {
            val attempts = state.recentAttempts
            val current = Difficulty.clamp(state.currentDifficulty)
            if (attempts.isEmpty()) return Decision(current, RecommendationReason.START)

            // 규칙4(정체): 현재 난이도에서 누적 오답이 임계 이상이면 해설 + 선수 개념(난이도 −1)으로.
            val wrongAtCurrent =
                attempts.count { attempt ->
                    !attempt.isCorrect && problemsById[attempt.problemId]?.difficulty == current
                }
            if (wrongAtCurrent >= RecommendationRules.STAGNATION_WRONG) {
                return Decision(Difficulty.clamp(current - 1), RecommendationReason.REMEDIATION)
            }

            // 규칙1(상승): 최근 연속 정답.
            val trailingCorrect = attempts.takeLastWhile { it.isCorrect }.size
            if (trailingCorrect >= RecommendationRules.PROMOTE_STREAK) {
                return Decision(Difficulty.clamp(current + 1), RecommendationReason.ADVANCED)
            }

            // 규칙2(하강): 최근 연속 오답.
            val trailingWrong = attempts.takeLastWhile { !it.isCorrect }.size
            if (trailingWrong >= RecommendationRules.DEMOTE_STREAK) {
                return Decision(Difficulty.clamp(current - 1), RecommendationReason.RETREATED)
            }

            // 규칙3(혼조): 같은 난이도 유지.
            return Decision(current, RecommendationReason.STAY)
        }

        // 규칙6: 목표 난이도 그룹을 고르되, 해당 난이도가 비어 있으면 난이도 차가 가장 작은 그룹으로 폴백.
        private fun selectGroup(
            groups: List<ProblemGroup>,
            difficulty: Int,
            random: Random,
        ): ProblemGroup? {
            val nonEmpty = groups.filter { it.problems.isNotEmpty() }
            if (nonEmpty.isEmpty()) return null
            val exact = nonEmpty.filter { it.difficulty == difficulty }
            if (exact.isNotEmpty()) return exact.random(random)
            val nearestDelta = nonEmpty.minOf { abs(it.difficulty - difficulty) }
            return nonEmpty.filter { abs(it.difficulty - difficulty) == nearestDelta }.random(random)
        }

        // 규칙5: 그룹 내 최근에 풀지 않은 문제 중 랜덤. 모두 최근에 풀었다면 그룹 전체에서 랜덤.
        private fun selectProblem(
            group: ProblemGroup,
            recentAttempts: List<Attempt>,
            random: Random,
        ): Problem? {
            if (group.problems.isEmpty()) return null
            val solvedRecently = recentAttempts.mapTo(mutableSetOf()) { it.problemId }
            val unsolved = group.problems.filter { it.id !in solvedRecently }
            val pool = unsolved.ifEmpty { group.problems }
            return pool.random(random)
        }
    }
