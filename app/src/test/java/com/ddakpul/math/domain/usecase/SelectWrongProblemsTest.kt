package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.model.MathArea
import com.ddakpul.math.domain.usecase.TestFixtures.attempt
import com.ddakpul.math.domain.usecase.TestFixtures.problem
import com.google.common.truth.Truth.assertThat
import org.junit.Test

class SelectWrongProblemsTest {
    private val problems =
        listOf(
            problem("num1", difficulty = 2, area = MathArea.NUMBER_OPERATION),
            problem("num2", difficulty = 3, area = MathArea.NUMBER_OPERATION),
            problem("geo1", difficulty = 2, area = MathArea.SHAPE_MEASUREMENT),
        )
    private val problemsById = problems.associateBy { it.id }

    @Test
    fun onlyLatestWrongPerProblem_newestFirst() {
        val result =
            selectWrongProblems(
                listOf(
                    attempt("num1", false, timestamp = 100), // num1 틀림…
                    attempt("num1", true, timestamp = 101), // …다시 맞힘 → 오답 노트에서 졸업
                    attempt("num2", true, timestamp = 102),
                    attempt("num2", false, timestamp = 103), // 최근 시도가 오답 → 포함
                    attempt("geo1", false, timestamp = 104), // 최근 오답 → 포함
                ),
                problemsById,
            )

        assertThat(result.map { it.problem.id }).containsExactly("geo1", "num2").inOrder()
        assertThat(result.first().lastWrongAt).isEqualTo(104)
    }

    @Test
    fun wrongCount_countsEveryIncorrectAttempt() {
        val result =
            selectWrongProblems(
                listOf(
                    attempt("num1", false, timestamp = 100),
                    attempt("num1", true, timestamp = 101), // 중간에 한 번 맞혀도…
                    attempt("num1", false, timestamp = 102), // …마지막이 오답이면 포함, 오답 횟수는 2
                ),
                problemsById,
            )

        val entry = result.single { it.problem.id == "num1" }
        assertThat(entry.wrongCount).isEqualTo(2)
        assertThat(entry.lastWrongAt).isEqualTo(102)
    }

    @Test
    fun notCapped_andSkipsProblemsMissingFromBank() {
        val result =
            selectWrongProblems(
                listOf(
                    attempt("num1", false, timestamp = 100),
                    attempt("num2", false, timestamp = 101),
                    attempt("geo1", false, timestamp = 102),
                    attempt("ghost", false, timestamp = 103), // 은행에 없는 문제 → 제외
                ),
                problemsById,
            )

        // 리포트 카드(6개 제한)와 달리 전부 담고, 은행에 없는 문제는 빠진다.
        assertThat(result.map { it.problem.id }).containsExactly("geo1", "num2", "num1").inOrder()
    }

    @Test
    fun empty_whenNoAttemptsOrAllCorrect() {
        assertThat(selectWrongProblems(emptyList(), problemsById)).isEmpty()
        assertThat(
            selectWrongProblems(
                listOf(attempt("num1", true, timestamp = 100)),
                problemsById,
            ),
        ).isEmpty()
    }
}
