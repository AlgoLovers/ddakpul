package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.model.GradingResult
import com.ddakpul.math.domain.model.Problem
import javax.inject.Inject

/**
 * 선택한 보기를 채점한다. 오답이면서 알려진 흔한 오답이면 맞춤 오개념 피드백을 함께 돌려준다.
 * 순수 함수 — 부수효과 없음.
 */
class GradeAttemptUseCase
    @Inject
    constructor() {
        operator fun invoke(
            problem: Problem,
            selectedIndex: Int,
        ): GradingResult {
            val correctIndex = problem.answer.correctChoiceIndex
            val isCorrect = selectedIndex == correctIndex
            val mistake =
                if (isCorrect) {
                    null
                } else {
                    problem.commonMistakes.firstOrNull { it.choiceIndex == selectedIndex }
                }
            return GradingResult(
                problem = problem,
                selectedIndex = selectedIndex,
                correctIndex = correctIndex,
                isCorrect = isCorrect,
                mistake = mistake,
                explanation = problem.explanation,
                detailedExplanation = problem.detailedExplanation,
            )
        }
    }
