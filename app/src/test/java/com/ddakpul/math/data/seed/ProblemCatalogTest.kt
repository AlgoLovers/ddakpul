package com.ddakpul.math.data.seed

import com.ddakpul.math.data.local.seed.ProblemCatalog
import com.ddakpul.math.domain.model.Difficulty
import com.google.common.truth.Truth.assertThat
import org.junit.Test

/**
 * 내장 문제은행의 무결성 검사. 콘텐츠를 추가·수정할 때 실수(정답 인덱스 이탈,
 * 오답 매핑 오류, 그룹 불일치)를 컴파일 타임처럼 잡아주는 안전망.
 */
class ProblemCatalogTest {
    private val problems = ProblemCatalog.problems
    private val groups = problems.groupBy { it.groupId }

    @Test
    fun idsAreUnique() {
        val duplicates = problems.groupBy { it.id }.filterValues { it.size > 1 }.keys
        assertThat(duplicates).isEmpty()
    }

    @Test
    fun everyProblemHasFourChoices_andValidAnswerIndex() {
        problems.forEach { problem ->
            assertThat(problem.choices).hasSize(4)
            assertThat(problem.answer.correctChoiceIndex).isIn(problem.choices.indices)
        }
    }

    @Test
    fun mistakesPointToExistingWrongChoices() {
        problems.forEach { problem ->
            problem.commonMistakes.forEach { mistake ->
                assertThat(mistake.choiceIndex).isIn(problem.choices.indices)
                // 오개념 피드백이 정답 보기에 붙어 있으면 안 된다.
                assertThat(mistake.choiceIndex).isNotEqualTo(problem.answer.correctChoiceIndex)
                assertThat(mistake.misconception).isNotEmpty()
            }
        }
    }

    @Test
    fun groupsShareSameDifficultyAndArea() {
        groups.forEach { (groupId, inGroup) ->
            assertThat(inGroup.map { it.difficulty }.distinct()).hasSize(1)
            assertThat(inGroup.map { it.area }.distinct()).hasSize(1)
        }
    }

    @Test
    fun everyProblemHasExplanation() {
        // 아이가 어떤 문제를 틀려도 풀이(생각의 경로)를 볼 수 있어야 한다 — 정답만 보여주는 문제 금지.
        problems.forEach { problem ->
            assertThat(problem.explanation.orEmpty().length).isAtLeast(MIN_EXPLANATION_LENGTH)
        }
    }

    @Test
    fun everyGroupHasEnoughProblemsForVariety() {
        // 규칙5(최근에 안 푼 문제 중 랜덤)가 의미 있으려면 그룹당 최소 3문항.
        groups.forEach { (groupId, inGroup) ->
            assertThat(inGroup.size).isAtLeast(3)
        }
    }

    @Test
    fun allDifficultiesArePresent() {
        val difficulties = problems.map { it.difficulty }.distinct().sorted()
        assertThat(difficulties).containsAtLeastElementsIn(Difficulty.MIN..Difficulty.MAX)
    }

    @Test
    fun difficultiesAreWithinBounds() {
        problems.forEach { problem ->
            assertThat(problem.difficulty).isAtLeast(Difficulty.MIN)
            assertThat(problem.difficulty).isAtMost(Difficulty.MAX)
        }
    }

    @Test
    fun statementsAndChoicesAreNotBlank() {
        problems.forEach { problem ->
            assertThat(problem.statement).isNotEmpty()
            problem.choices.forEach { choice -> assertThat(choice).isNotEmpty() }
            assertThat(problem.conceptTags).isNotEmpty()
        }
    }

    private companion object {
        /** 한 줄 스텁("정답은 X")이 풀이 행세를 못 하게 하는 최소 길이. */
        const val MIN_EXPLANATION_LENGTH = 20
    }
}
