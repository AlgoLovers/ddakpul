package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.model.Answer
import com.ddakpul.math.domain.model.Cell
import com.ddakpul.math.domain.model.DissectionPuzzle
import com.ddakpul.math.domain.model.MathArea
import com.ddakpul.math.domain.usecase.TestFixtures.attempt
import com.ddakpul.math.domain.usecase.TestFixtures.group
import com.ddakpul.math.domain.usecase.TestFixtures.problem
import com.ddakpul.math.domain.usecase.TestFixtures.standardGroups
import com.google.common.truth.Truth.assertThat
import org.junit.Test
import kotlin.random.Random

class SelectWorksheetProblemsTest {
    private val random = Random(7)

    @Test
    fun respectsRequestedCount() {
        val result =
            selectWorksheetProblems(
                spec = WorksheetSpec(count = 5, source = WorksheetSource.RECOMMENDED),
                groups = standardGroups(),
                recentAttempts = emptyList(),
                currentDifficulty = 3,
                random = random,
            )

        assertThat(result).hasSize(5)
        assertThat(result.map { it.id }.distinct()).hasSize(5)
    }

    @Test
    fun areaFilter_onlyIncludesThatArea() {
        val groups =
            listOf(
                group(difficulty = 2, problems = listOf(problem("n1", 2), problem("n2", 2)), id = "g-num"),
                group(
                    difficulty = 2,
                    problems =
                        listOf(
                            problem("s1", 2, area = MathArea.SHAPE_MEASUREMENT, groupId = "g-shape"),
                            problem("s2", 2, area = MathArea.SHAPE_MEASUREMENT, groupId = "g-shape"),
                        ),
                    id = "g-shape",
                    area = MathArea.SHAPE_MEASUREMENT,
                ),
            )

        val result =
            selectWorksheetProblems(
                spec = WorksheetSpec(count = 10, source = WorksheetSource.RECOMMENDED, area = MathArea.SHAPE_MEASUREMENT),
                groups = groups,
                recentAttempts = emptyList(),
                currentDifficulty = 2,
                random = random,
            )

        assertThat(result).isNotEmpty()
        assertThat(result.all { it.area == MathArea.SHAPE_MEASUREMENT }).isTrue()
    }

    @Test
    fun wrongFirst_includesRecentlyWrongProblems() {
        val attempts =
            listOf(
                attempt("d3-1", isCorrect = false, timestamp = 1),
                attempt("d3-2", isCorrect = true, timestamp = 2),
                attempt("d4-1", isCorrect = false, timestamp = 3),
            )

        val result =
            selectWorksheetProblems(
                spec = WorksheetSpec(count = 6, source = WorksheetSource.WRONG_FIRST),
                groups = standardGroups(),
                recentAttempts = attempts,
                currentDifficulty = 3,
                random = random,
            )

        val ids = result.map { it.id }
        assertThat(ids).containsAtLeast("d3-1", "d4-1")
    }

    @Test
    fun recommended_prefersProblemsNotSolvedRecently() {
        // 난이도 3 그룹 3문제 중 2문제를 이미 풀었고 2문제만 필요하면, 안 푼 문제가 반드시 포함된다.
        val attempts = listOf(attempt("d3-1", true), attempt("d3-2", true))

        val result =
            selectWorksheetProblems(
                spec = WorksheetSpec(count = 2, source = WorksheetSource.RECOMMENDED),
                groups = standardGroups(),
                recentAttempts = attempts,
                currentDifficulty = 3,
                random = random,
            )

        // 밴드(2~4)에는 안 푼 문제가 7개나 있으므로 최근에 푼 문제는 뽑히지 않는다.
        assertThat(result.map { it.id }).containsNoneOf("d3-1", "d3-2")
    }

    @Test
    fun interleaves_sameGroupNotAdjacentWhenAvoidable() {
        val groups =
            listOf(
                group(difficulty = 3, problems = (1..3).map { problem("a$it", 3, groupId = "g-a") }, id = "g-a"),
                group(difficulty = 3, problems = (1..3).map { problem("b$it", 3, groupId = "g-b") }, id = "g-b"),
            )

        val result =
            selectWorksheetProblems(
                spec = WorksheetSpec(count = 6, source = WorksheetSource.RECOMMENDED),
                groups = groups,
                recentAttempts = emptyList(),
                currentDifficulty = 3,
                random = random,
            )

        assertThat(result).hasSize(6)
        result.zipWithNext().forEach { (first, second) ->
            assertThat(first.groupId).isNotEqualTo(second.groupId)
        }
    }

    @Test
    fun emptyBank_returnsEmpty() {
        val result =
            selectWorksheetProblems(
                spec = WorksheetSpec(count = 10, source = WorksheetSource.RECOMMENDED),
                groups = emptyList(),
                recentAttempts = emptyList(),
                currentDifficulty = 3,
                random = random,
            )

        assertThat(result).isEmpty()
    }

    @Test
    fun bankSmallerThanCount_returnsWholeBank() {
        val groups = listOf(group(difficulty = 3, problems = listOf(problem("q1", 3), problem("q2", 3))))

        val result =
            selectWorksheetProblems(
                spec = WorksheetSpec(count = 10, source = WorksheetSource.RECOMMENDED),
                groups = groups,
                recentAttempts = emptyList(),
                currentDifficulty = 3,
                random = random,
            )

        assertThat(result).hasSize(2)
    }

    @Test
    fun excludesDissectionPuzzles() {
        // 구성형(등분 퍼즐)은 종이에 옮길 수 없고, 정답지 생성이 인덱스 −1로 크래시했다(2026-08 QA).
        val puzzle =
            problem("d1", 3).copy(
                choices = emptyList(),
                answer = Answer(-1),
                dissection = DissectionPuzzle(cells = listOf(Cell(0, 0), Cell(0, 1)), pieceCount = 2),
            )
        val groups =
            listOf(
                group(difficulty = 3, problems = listOf(puzzle, problem("n1", 3)), id = "g-mixed"),
            )

        val result =
            selectWorksheetProblems(
                spec = WorksheetSpec(count = 5, source = WorksheetSource.RECOMMENDED),
                groups = groups,
                recentAttempts = emptyList(),
                currentDifficulty = 3,
                random = random,
            )

        assertThat(result.map { it.id }).containsExactly("n1")
    }

    @Test
    fun wrongFirst_alsoExcludesDissectionPuzzles() {
        val puzzle =
            problem("d1", 3).copy(
                choices = emptyList(),
                answer = Answer(-1),
                dissection = DissectionPuzzle(cells = listOf(Cell(0, 0), Cell(0, 1)), pieceCount = 2),
            )
        val groups = listOf(group(difficulty = 3, problems = listOf(puzzle, problem("n1", 3)), id = "g-mixed"))

        val result =
            selectWorksheetProblems(
                spec = WorksheetSpec(count = 5, source = WorksheetSource.WRONG_FIRST),
                groups = groups,
                recentAttempts = listOf(attempt("d1", false)),
                currentDifficulty = 3,
                random = random,
            )

        assertThat(result.map { it.id }).doesNotContain("d1")
    }
}
