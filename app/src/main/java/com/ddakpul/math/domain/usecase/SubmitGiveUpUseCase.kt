package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.model.GradingResult
import com.ddakpul.math.domain.model.Problem
import javax.inject.Inject

/**
 * "모르겠어요" — 답을 고르지 않고 풀이를 본다. 못 푼 것이므로 **오답으로 기록**해(추천 난이도가
 * 자연스럽게 아이 수준으로 내려가고, 오답 노트에 담겨 다음에 다시 학습된다) 풀이가 담긴 결과를 돌려준다.
 * 고른 답이 없으므로 [GradingResult.selectedIndex]는 null이고 오개념 피드백([mistake])도 없다.
 */
class SubmitGiveUpUseCase
    @Inject
    constructor(
        private val recordAttempt: RecordAttemptUseCase,
    ) {
        suspend operator fun invoke(
            problem: Problem,
            timeSpentSec: Int,
            timestamp: Long,
            reviewMode: Boolean = false,
        ): GradingResult {
            recordAttempt(
                problem = problem,
                isCorrect = false,
                timeSpentSec = timeSpentSec,
                timestamp = timestamp,
                reviewMode = reviewMode,
            )
            return GradingResult(
                problem = problem,
                selectedIndex = null,
                correctIndex = problem.answer.correctChoiceIndex,
                isCorrect = false,
                mistake = null,
                explanation = problem.explanation,
                detailedExplanation = problem.detailedExplanation,
            )
        }
    }
