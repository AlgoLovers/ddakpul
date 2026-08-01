package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.model.Difficulty
import com.ddakpul.math.domain.model.MathArea
import com.ddakpul.math.domain.model.RecommendationReason
import com.ddakpul.math.domain.usecase.TestFixtures.attempt
import com.ddakpul.math.domain.usecase.TestFixtures.group
import com.ddakpul.math.domain.usecase.TestFixtures.problem
import com.ddakpul.math.domain.usecase.TestFixtures.standardGroups
import com.ddakpul.math.domain.usecase.TestFixtures.state
import com.google.common.truth.Truth.assertThat
import org.junit.Test
import kotlin.random.Random

/** CLAUDE.md 추천 규칙 1~6을 각각 검증한다. */
class RecommendNextProblemUseCaseTest {
    private val recommend = RecommendNextProblemUseCase()
    private val seededRandom = Random(42)

    @Test
    fun noHistory_startsAtCurrentDifficulty() {
        val result = recommend(state(currentDifficulty = 3), standardGroups(), seededRandom)

        assertThat(result).isNotNull()
        assertThat(result!!.reason).isEqualTo(RecommendationReason.START)
        assertThat(result.targetDifficulty).isEqualTo(3)
    }

    @Test
    fun rule1_twoConsecutiveCorrect_promotesDifficulty() {
        val attempts = listOf(attempt("d3-1", true), attempt("d3-2", true))

        val result = recommend(state(currentDifficulty = 3, recentAttempts = attempts), standardGroups(), seededRandom)

        assertThat(result!!.reason).isEqualTo(RecommendationReason.ADVANCED)
        assertThat(result.targetDifficulty).isEqualTo(4)
    }

    @Test
    fun rule2_twoConsecutiveWrong_demotesDifficulty() {
        val attempts = listOf(attempt("d3-1", false), attempt("d3-2", false))

        val result = recommend(state(currentDifficulty = 3, recentAttempts = attempts), standardGroups(), seededRandom)

        assertThat(result!!.reason).isEqualTo(RecommendationReason.RETREATED)
        assertThat(result.targetDifficulty).isEqualTo(2)
    }

    @Test
    fun rule3_mixedResults_staysAtSameDifficulty() {
        // 맞았다 틀렸다(혼조) — 연속 임계에도, 정체 임계에도 못 미친다.
        val attempts = listOf(attempt("d3-1", false), attempt("d3-2", true))

        val result = recommend(state(currentDifficulty = 3, recentAttempts = attempts), standardGroups(), seededRandom)

        assertThat(result!!.reason).isEqualTo(RecommendationReason.STAY)
        assertThat(result.targetDifficulty).isEqualTo(3)
    }

    @Test
    fun rule4_accumulatedWrongAtSameDifficulty_triggersRemediationWithExplanation() {
        // 같은 난이도에서 누적 오답 3회(연속이 아니어도) → 정체 감지.
        val attempts =
            listOf(
                attempt("d3-1", false),
                attempt("d3-2", true),
                attempt("d3-3", false),
                attempt("d3-1", true),
                attempt("d3-2", false),
            )

        val result = recommend(state(currentDifficulty = 3, recentAttempts = attempts), standardGroups(), seededRandom)

        assertThat(result!!.reason).isEqualTo(RecommendationReason.REMEDIATION)
        assertThat(result.targetDifficulty).isEqualTo(2)
        assertThat(result.showExplanation).isTrue()
    }

    @Test
    fun rule4_recoveringStreak_promotesInsteadOfRemediation() {
        // 오답 3개가 최근 창에 남아 있어도 마지막이 2연속 정답이면 정체가 아니라 회복 — 승급이 이긴다.
        // ("연속으로 다 맞히는데도 난이도가 떨어져요" 사용자 피드백 재현 방지, 2026-08.)
        val attempts =
            listOf(
                attempt("d3-1", false),
                attempt("d3-2", false),
                attempt("d3-3", false),
                attempt("d3-1", true),
                attempt("d3-2", true),
            )

        val result = recommend(state(currentDifficulty = 3, recentAttempts = attempts), standardGroups(), seededRandom)

        assertThat(result!!.reason).isEqualTo(RecommendationReason.ADVANCED)
        assertThat(result.targetDifficulty).isEqualTo(4)
    }

    @Test
    fun rule4_lastAnswerCorrect_staysWithoutRemediation() {
        // 누적 오답이 임계(3)에 닿아도 직전 한 문제를 맞혔으면 막힌 상태가 아니다 — 강등하지 않는다.
        val attempts =
            listOf(
                attempt("d3-1", false),
                attempt("d3-2", false),
                attempt("d3-3", false),
                attempt("d3-1", true),
            )

        val result = recommend(state(currentDifficulty = 3, recentAttempts = attempts), standardGroups(), seededRandom)

        assertThat(result!!.reason).isEqualTo(RecommendationReason.STAY)
        assertThat(result.targetDifficulty).isEqualTo(3)
    }

    @Test
    fun rule5_picksProblemNotSolvedRecently() {
        // 난이도 3 그룹에 q1,q2,q3. 최근에 q1,q2를 풀었으므로 q3가 나와야 한다.
        val groups =
            listOf(
                group(
                    difficulty = 3,
                    problems =
                        listOf(
                            problem("q1", 3),
                            problem("q2", 3),
                            problem("q3", 3),
                        ),
                ),
            )
        // q1(정답)·q2(오답) 혼조 → 난이도 유지. 직전 오답이므로 규칙7(재도전)이 같은 그룹에서
        // 최근에 안 푼 q3를 낸다 — 규칙5(안 푼 문제 우선)와 규칙7이 함께 작동하는 경로.
        val attempts = listOf(attempt("q1", true), attempt("q2", false))

        val result = recommend(state(currentDifficulty = 3, recentAttempts = attempts), groups, seededRandom)

        assertThat(result!!.reason).isEqualTo(RecommendationReason.RETRY)
        assertThat(result.problem.id).isEqualTo("q3")
    }

    @Test
    fun rule5_whenAllSolvedRecently_fallsBackToWholeGroup() {
        val groups = listOf(group(difficulty = 3, problems = listOf(problem("q1", 3), problem("q2", 3))))
        val attempts = listOf(attempt("q1", true), attempt("q2", false))

        val result = recommend(state(currentDifficulty = 3, recentAttempts = attempts), groups, seededRandom)

        // 모두 최근에 풀었더라도 null이 아니라 그룹 전체에서 하나를 낸다.
        assertThat(result).isNotNull()
        assertThat(result!!.problem.id).isAnyOf("q1", "q2")
    }

    @Test
    fun rule6_promotionIsClampedAtMax() {
        val attempts = listOf(attempt("d5-1", true), attempt("d5-2", true))

        val result = recommend(state(currentDifficulty = Difficulty.MAX, recentAttempts = attempts), standardGroups(), seededRandom)

        assertThat(result!!.reason).isEqualTo(RecommendationReason.ADVANCED)
        assertThat(result.targetDifficulty).isEqualTo(Difficulty.MAX)
    }

    @Test
    fun rule6_demotionIsClampedAtMin() {
        val attempts = listOf(attempt("d1-1", false), attempt("d1-2", false))

        val result = recommend(state(currentDifficulty = 1, recentAttempts = attempts), standardGroups(), seededRandom)

        assertThat(result!!.reason).isEqualTo(RecommendationReason.RETREATED)
        assertThat(result.targetDifficulty).isEqualTo(1)
    }

    @Test
    fun emptyGroups_returnsNull() {
        val result = recommend(state(currentDifficulty = 3), emptyList(), seededRandom)

        assertThat(result).isNull()
    }

    // ── 규칙7 (v0.3): 오답 직후 같은 그룹 재도전 ─────────────────────────────────

    @Test
    fun rule7_lastWrong_retriesDifferentProblemFromSameGroup() {
        val groups =
            listOf(
                group(difficulty = 3, problems = (1..3).map { problem("a$it", 3, groupId = "g-a") }, id = "g-a"),
                group(difficulty = 3, problems = (1..3).map { problem("b$it", 3, groupId = "g-b") }, id = "g-b"),
            )
        // 혼조(정답 후 오답) — 직전 오답은 g-a 그룹의 a1.
        val attempts = listOf(attempt("b1", true), attempt("a1", false))

        val result = recommend(state(currentDifficulty = 3, recentAttempts = attempts), groups, seededRandom)

        assertThat(result!!.reason).isEqualTo(RecommendationReason.RETRY)
        assertThat(result.group.id).isEqualTo("g-a")
        assertThat(result.problem.id).isNotEqualTo("a1")
    }

    @Test
    fun rule7_notTriggered_whenLastAttemptCorrect() {
        val attempts = listOf(attempt("d3-1", false), attempt("d3-2", true))

        val result = recommend(state(currentDifficulty = 3, recentAttempts = attempts), standardGroups(), seededRandom)

        assertThat(result!!.reason).isEqualTo(RecommendationReason.STAY)
    }

    @Test
    fun stay_avoidsRepeatingSameGroupTypeConsecutively() {
        val groups =
            listOf(
                group(difficulty = 3, problems = (1..3).map { problem("a$it", 3, groupId = "g-a") }, id = "g-a"),
                group(difficulty = 3, problems = (1..3).map { problem("b$it", 3, groupId = "g-b") }, id = "g-b"),
            )
        // 혼조 유지(STAY) + 직전이 정답이라 재도전 아님 — 직전 문제 a1은 g-a 소속.
        val attempts = listOf(attempt("b1", false), attempt("a1", true))

        val result = recommend(state(currentDifficulty = 3, recentAttempts = attempts), groups, seededRandom)

        assertThat(result!!.reason).isEqualTo(RecommendationReason.STAY)
        // 같은 유형(g-a)이 연달아 나오지 않고 다른 그룹(g-b)에서 출제된다.
        assertThat(result.group.id).isEqualTo("g-b")
    }

    @Test
    fun rule7_doesNotOverrideDemotion() {
        // 연속 2오답이면 재도전이 아니라 규칙2(하강)가 우선.
        val attempts = listOf(attempt("d3-1", false), attempt("d3-2", false))

        val result = recommend(state(currentDifficulty = 3, recentAttempts = attempts), standardGroups(), seededRandom)

        assertThat(result!!.reason).isEqualTo(RecommendationReason.RETREATED)
    }

    // ── 규칙8 (v0.3): 복습 슬롯 배합 ─────────────────────────────────────────────

    @Test
    fun rule8_reviewSlot_servesDueGroupWithoutChangingDifficulty() {
        // todaySolved=2 → 3번째 문제가 복습 슬롯(2 % 3 == 2).
        val result =
            recommend(
                state(currentDifficulty = 4),
                standardGroups(),
                seededRandom,
                reviewDueGroupIds = listOf("g-2"),
                todaySolved = 2,
            )

        assertThat(result!!.reason).isEqualTo(RecommendationReason.REVIEW)
        assertThat(result.group.id).isEqualTo("g-2")
        assertThat(result.problem.difficulty).isEqualTo(2)
        // 복습은 현재 난이도를 건드리지 않는다.
        assertThat(result.targetDifficulty).isEqualTo(4)
    }

    @Test
    fun rule8_notReviewSlotPosition_normalFlow() {
        val result =
            recommend(
                state(currentDifficulty = 4),
                standardGroups(),
                seededRandom,
                reviewDueGroupIds = listOf("g-2"),
                todaySolved = 1,
            )

        assertThat(result!!.reason).isEqualTo(RecommendationReason.START)
        assertThat(result.targetDifficulty).isEqualTo(4)
    }

    @Test
    fun rule8_remediationTakesPriorityOverReview() {
        // 현재 난이도에서 누적 오답 3회(정체)면 복습 슬롯이어도 처치가 우선.
        val attempts =
            listOf(
                attempt("d3-1", false),
                attempt("d3-2", true),
                attempt("d3-3", false),
                attempt("d3-1", false),
            )

        val result =
            recommend(
                state(currentDifficulty = 3, recentAttempts = attempts),
                standardGroups(),
                seededRandom,
                reviewDueGroupIds = listOf("g-1"),
                todaySolved = 2,
            )

        assertThat(result!!.reason).isEqualTo(RecommendationReason.REMEDIATION)
    }

    @Test
    fun rule8_emptyReviewQueue_normalFlowEvenOnSlot() {
        val result =
            recommend(
                state(currentDifficulty = 3),
                standardGroups(),
                seededRandom,
                reviewDueGroupIds = emptyList(),
                todaySolved = 2,
            )

        assertThat(result!!.reason).isEqualTo(RecommendationReason.START)
    }

    // ── 규칙5 (개정): 같은 문제 하루 중복 금지 + 영역 균형 ────────────────────────

    @Test
    fun rule5_excludesProblemsAlreadySolvedToday() {
        val groups =
            listOf(group(difficulty = 3, problems = listOf(problem("q1", 3), problem("q2", 3), problem("q3", 3))))
        // 기록 없음(START)이라 난이도/재도전 분기 없이 선택 로직만 탄다. 오늘 q1·q2는 이미 냈다.
        val result =
            recommend(
                state(currentDifficulty = 3),
                groups,
                seededRandom,
                todayProblemIds = listOf("q1", "q2"),
            )

        assertThat(result!!.problem.id).isEqualTo("q3")
    }

    @Test
    fun rule5_wholeGroupSolvedToday_stillReturnsBestEffort() {
        val groups = listOf(group(difficulty = 3, problems = listOf(problem("q1", 3), problem("q2", 3))))
        val result =
            recommend(
                state(currentDifficulty = 3),
                groups,
                seededRandom,
                todayProblemIds = listOf("q1", "q2"),
            )

        // 그룹을 오늘 다 냈어도 막다른 길(null) 대신 하나를 낸다 — 문제은행이 얇을 때의 best-effort.
        assertThat(result).isNotNull()
        assertThat(result!!.problem.id).isAnyOf("q1", "q2")
    }

    @Test
    fun rule5_balancesAcrossAreas_prefersLeastServedAreaToday() {
        val groups =
            listOf(
                group(
                    difficulty = 3,
                    id = "g-num",
                    area = MathArea.NUMBER_OPERATION,
                    problems = (1..3).map { problem("num$it", 3, area = MathArea.NUMBER_OPERATION, groupId = "g-num") },
                ),
                group(
                    difficulty = 3,
                    id = "g-geo",
                    area = MathArea.SHAPE_MEASUREMENT,
                    problems = (1..3).map { problem("geo$it", 3, area = MathArea.SHAPE_MEASUREMENT, groupId = "g-geo") },
                ),
            )
        // 오늘 수와연산을 2번, 도형을 0번 냈다 → 적게 낸 도형 영역에서 나와야 한다.
        val result =
            recommend(
                state(currentDifficulty = 3),
                groups,
                seededRandom,
                todayProblemIds = listOf("num1", "num2"),
            )

        assertThat(result!!.group.area).isEqualTo(MathArea.SHAPE_MEASUREMENT)
        assertThat(result.problem.id).startsWith("geo")
    }
}
