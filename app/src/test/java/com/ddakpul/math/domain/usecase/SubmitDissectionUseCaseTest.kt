package com.ddakpul.math.domain.usecase

import com.ddakpul.math.data.FakeLearnerRepository
import com.ddakpul.math.domain.model.Answer
import com.ddakpul.math.domain.model.Cell
import com.ddakpul.math.domain.model.DissectionPuzzle
import com.ddakpul.math.domain.model.MathArea
import com.ddakpul.math.domain.model.Problem
import com.google.common.truth.Truth.assertThat
import kotlinx.coroutines.test.runTest
import org.junit.Test

class SubmitDissectionUseCaseTest {
    private val learner = FakeLearnerRepository()
    private val submit = SubmitDissectionUseCase(learner, ValidateDissectionUseCase())

    private val puzzle =
        DissectionPuzzle(
            cells = listOf(Cell(0, 0), Cell(0, 1), Cell(0, 2), Cell(1, 0), Cell(1, 1), Cell(1, 2)),
            pieceCount = 3,
        )
    private val problem =
        Problem(
            id = "dissect-x",
            area = MathArea.SHAPE_MEASUREMENT,
            conceptTags = listOf("합동 등분"),
            difficulty = 3,
            groupId = "g-dissect-3",
            statement = "나눠 보세요",
            choices = emptyList(),
            answer = Answer(-1),
            explanation = null,
            commonMistakes = emptyList(),
            dissection = puzzle,
        )

    @Test
    fun correctAnswer_recordsCorrectAttempt() =
        runTest {
            val assign =
                mapOf(
                    Cell(0, 0) to 0,
                    Cell(1, 0) to 0,
                    Cell(0, 1) to 1,
                    Cell(1, 1) to 1,
                    Cell(0, 2) to 2,
                    Cell(1, 2) to 2,
                )
            val result = submit(problem, assign, timeSpentSec = 30, timestamp = 1_000L)
            assertThat(result.isValid).isTrue()
            assertThat(learner.recordedAttempts).hasSize(1)
            assertThat(learner.recordedAttempts.first().isCorrect).isTrue()
            assertThat(learner.recordedAttempts.first().problemId).isEqualTo("dissect-x")
        }

    @Test
    fun wrongAnswer_recordsIncorrectAttempt() =
        runTest {
            // 끊긴 조각(대각선 배정) — 확실히 틀린 답
            val assign =
                mapOf(
                    Cell(0, 0) to 0,
                    Cell(1, 1) to 0,
                    Cell(0, 1) to 1,
                    Cell(1, 0) to 1,
                    Cell(0, 2) to 2,
                    Cell(1, 2) to 2,
                )
            val result = submit(problem, assign, timeSpentSec = 30, timestamp = 1_000L)
            assertThat(result.isValid).isFalse()
            assertThat(result.error).isEqualTo(DissectionError.DISCONNECTED)
            assertThat(learner.recordedAttempts).hasSize(1)
            assertThat(learner.recordedAttempts.first().isCorrect).isFalse()
        }

    @Test
    fun nonDissectionProblem_returnsIncompleteWithoutCrash() =
        runTest {
            val mc = problem.copy(dissection = null)
            val result = submit(mc, emptyMap(), timeSpentSec = 0, timestamp = 0L)
            assertThat(result.isValid).isFalse()
            assertThat(result.error).isEqualTo(DissectionError.INCOMPLETE)
        }
}
