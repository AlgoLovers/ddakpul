package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.usecase.TestFixtures.attempt
import com.ddakpul.math.domain.usecase.TestFixtures.group
import com.ddakpul.math.domain.usecase.TestFixtures.problem
import com.google.common.truth.Truth.assertThat
import org.junit.Test

class ComputeReviewQueueTest {
    private val groups =
        listOf(
            group(difficulty = 2, problems = (1..3).map { problem("a$it", 2, groupId = "g-a") }, id = "g-a"),
            group(difficulty = 3, problems = (1..3).map { problem("b$it", 3, groupId = "g-b") }, id = "g-b"),
        )

    private fun queue(
        attempts: List<com.ddakpul.math.domain.model.Attempt>,
        todayDay: Long,
    ) = computeReviewQueue(
        attempts = attempts,
        groups = groups,
        zoneOffsetMillis = 0L,
        nowMillis = todayDay * DAY,
    )

    @Test
    fun masteredGroup_becomesDueAfterFirstInterval() {
        // 10일차에 연속 2정답으로 숙달(박스1) → 만기 11일차.
        val attempts =
            listOf(
                attempt("a1", true, timestamp = DAY * 10),
                attempt("a2", true, timestamp = DAY * 10 + HOUR),
            )

        assertThat(queue(attempts, todayDay = 10)).isEmpty()
        assertThat(queue(attempts, todayDay = 11)).containsExactly("g-a")
        assertThat(queue(attempts, todayDay = 15)).containsExactly("g-a")
    }

    @Test
    fun groupNeverMastered_isNeverDue() {
        // 정답-오답-정답: 연속 2정답이 없어 숙달 미달.
        val attempts =
            listOf(
                attempt("a1", true, timestamp = DAY * 10),
                attempt("a2", false, timestamp = DAY * 10 + HOUR),
                attempt("a3", true, timestamp = DAY * 10 + 2 * HOUR),
            )

        assertThat(queue(attempts, todayDay = 30)).isEmpty()
    }

    @Test
    fun successfulReview_promotesBoxAndExtendsInterval() {
        // 숙달(10일차, 박스1 → 만기 11일) → 11일차 복습 성공(박스2 → 만기 11+3=14일).
        val attempts =
            listOf(
                attempt("a1", true, timestamp = DAY * 10),
                attempt("a2", true, timestamp = DAY * 10 + HOUR),
                attempt("a3", true, timestamp = DAY * 11),
            )

        assertThat(queue(attempts, todayDay = 13)).isEmpty()
        assertThat(queue(attempts, todayDay = 14)).containsExactly("g-a")
    }

    @Test
    fun failedReview_demotesToFirstBox() {
        // 복습 성공으로 박스2(만기 14일)까지 갔다가 14일차 복습 실패 → 박스1(만기 15일).
        val attempts =
            listOf(
                attempt("a1", true, timestamp = DAY * 10),
                attempt("a2", true, timestamp = DAY * 10 + HOUR),
                attempt("a3", true, timestamp = DAY * 11),
                attempt("a1", false, timestamp = DAY * 14),
            )

        assertThat(queue(attempts, todayDay = 14)).isEmpty()
        assertThat(queue(attempts, todayDay = 15)).containsExactly("g-a")
    }

    @Test
    fun mostOverdueGroupComesFirst() {
        val attempts =
            listOf(
                // g-a: 5일차 숙달 → 만기 6일 (오늘 20일이면 14일 밀림)
                attempt("a1", true, timestamp = DAY * 5),
                attempt("a2", true, timestamp = DAY * 5 + HOUR),
                // g-b: 18일차 숙달 → 만기 19일 (오늘 20일이면 1일 밀림)
                attempt("b1", true, timestamp = DAY * 18),
                attempt("b2", true, timestamp = DAY * 18 + HOUR),
            )

        assertThat(queue(attempts, todayDay = 20)).containsExactly("g-a", "g-b").inOrder()
    }

    @Test
    fun attemptsOnUnknownProblems_areIgnored() {
        val attempts =
            listOf(
                attempt("ghost1", true, timestamp = DAY * 10),
                attempt("ghost2", true, timestamp = DAY * 10 + HOUR),
            )

        assertThat(queue(attempts, todayDay = 30)).isEmpty()
    }

    private companion object {
        const val HOUR = 3_600_000L
        const val DAY = 86_400_000L
    }
}
