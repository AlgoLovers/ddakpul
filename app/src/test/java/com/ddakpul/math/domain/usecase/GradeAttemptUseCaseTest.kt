package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.model.Mistake
import com.ddakpul.math.domain.usecase.TestFixtures.problem
import com.google.common.truth.Truth.assertThat
import org.junit.Test

class GradeAttemptUseCaseTest {
    private val grade = GradeAttemptUseCase()

    @Test
    fun correctChoice_isCorrectWithoutMistake() {
        val problem = problem(id = "p1", difficulty = 2, answerIndex = 1)

        val result = grade(problem, selectedIndex = 1)

        assertThat(result.isCorrect).isTrue()
        assertThat(result.mistake).isNull()
        assertThat(result.correctIndex).isEqualTo(1)
    }

    @Test
    fun wrongChoiceMatchingKnownMistake_returnsMisconception() {
        val problem =
            problem(
                id = "p1",
                difficulty = 2,
                answerIndex = 1,
                mistakes = listOf(Mistake(choiceIndex = 0, misconception = "받아올림을 빼먹었어요")),
            )

        val result = grade(problem, selectedIndex = 0)

        assertThat(result.isCorrect).isFalse()
        assertThat(result.mistake?.misconception).isEqualTo("받아올림을 빼먹었어요")
    }

    @Test
    fun wrongChoiceWithoutKnownMistake_hasNoMisconception() {
        val problem =
            problem(
                id = "p1",
                difficulty = 2,
                answerIndex = 1,
                mistakes = listOf(Mistake(choiceIndex = 0, misconception = "설명")),
            )

        // 오답이지만 알려진 오답(index 0)이 아닌 index 2를 골랐다.
        val result = grade(problem, selectedIndex = 2)

        assertThat(result.isCorrect).isFalse()
        assertThat(result.mistake).isNull()
    }
}
