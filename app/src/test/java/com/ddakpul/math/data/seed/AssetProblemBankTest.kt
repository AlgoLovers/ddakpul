package com.ddakpul.math.data.seed

import com.ddakpul.math.data.local.seed.ProblemCatalog
import com.ddakpul.math.data.local.seed.parseAssetProblems
import com.ddakpul.math.domain.model.Difficulty
import com.google.common.truth.Truth.assertThat
import org.junit.Test
import java.io.File

/**
 * 생성 파이프라인 산출물(assets/problems_generated.json)의 무결성 검사.
 * 생성기 자체 검증에 더해, 앱이 실제로 파싱하는 경로로 한 번 더 지킨다.
 */
class AssetProblemBankTest {
    private val problems =
        parseAssetProblems(File("src/main/assets/problems_generated.json").readText())
    private val groups = problems.groupBy { it.groupId }

    @Test
    fun bankIsNotEmpty_andParses() {
        assertThat(problems.size).isAtLeast(30)
    }

    @Test
    fun idsAreUnique_andDoNotCollideWithHandAuthoredCatalog() {
        assertThat(problems.groupBy { it.id }.filterValues { it.size > 1 }).isEmpty()
        val catalogIds = ProblemCatalog.problems.mapTo(mutableSetOf()) { it.id }
        assertThat(problems.filter { it.id in catalogIds }).isEmpty()
    }

    @Test
    fun everyProblemHasFourDistinctChoices_andValidAnswer() {
        problems.forEach { problem ->
            assertThat(problem.choices).hasSize(4)
            assertThat(problem.choices.distinct()).hasSize(4)
            assertThat(problem.answer.correctChoiceIndex).isIn(problem.choices.indices)
        }
    }

    @Test
    fun mistakesPointToWrongChoices() {
        problems.forEach { problem ->
            problem.commonMistakes.forEach { mistake ->
                assertThat(mistake.choiceIndex).isIn(problem.choices.indices)
                assertThat(mistake.choiceIndex).isNotEqualTo(problem.answer.correctChoiceIndex)
            }
        }
    }

    @Test
    fun groupsAreConsistent_andBigEnough() {
        groups.forEach { (_, inGroup) ->
            assertThat(inGroup.size).isAtLeast(3)
            assertThat(inGroup.map { it.difficulty }.distinct()).hasSize(1)
            assertThat(inGroup.map { it.area }.distinct()).hasSize(1)
        }
    }

    @Test
    fun everyProblemHasExplanation_generatedBankTeachesEveryTime() {
        problems.forEach { problem ->
            assertThat(problem.explanation).isNotEmpty()
        }
    }

    @Test
    fun difficultiesAreWithinBounds() {
        problems.forEach { problem ->
            assertThat(problem.difficulty).isAtLeast(Difficulty.MIN)
            assertThat(problem.difficulty).isAtMost(Difficulty.MAX)
        }
    }

    @Test
    fun figuresParseIntoTypedModel() {
        val withFigure = problems.filter { it.figure != null }
        assertThat(withFigure).isNotEmpty()
        withFigure.forEach { problem ->
            assertThat(problem.figure!!.params).isNotEmpty()
        }
    }
}
