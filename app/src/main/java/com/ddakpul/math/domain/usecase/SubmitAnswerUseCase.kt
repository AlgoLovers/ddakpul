package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.model.GradingResult
import com.ddakpul.math.domain.model.Problem
import javax.inject.Inject

/**
 * 답을 채점하고 그 시도를 기록한다. [timestamp]와 [timeSpentSec]은 presentation 계층에서
 * 주입받아 domain을 순수하게 유지한다.
 */
class SubmitAnswerUseCase
    @Inject
    constructor(
        private val recordAttempt: RecordAttemptUseCase,
        private val grade: GradeAttemptUseCase,
    ) {
        suspend operator fun invoke(
            problem: Problem,
            selectedIndex: Int,
            timeSpentSec: Int,
            timestamp: Long,
            reviewMode: Boolean = false,
        ): GradingResult {
            val result = grade(problem, selectedIndex)
            recordAttempt(
                problem = problem,
                isCorrect = result.isCorrect,
                timeSpentSec = timeSpentSec,
                timestamp = timestamp,
                reviewMode = reviewMode,
            )
            return result
        }
    }
