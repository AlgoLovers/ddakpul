package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.repository.ProblemFeedbackRepository
import javax.inject.Inject

/**
 * 문제를 "별로예요"로 제외한다. 제외된 문제는 추천·학습지에서 다시 나오지 않는다.
 * 시각([timestampMillis])은 호출부가 주입해 domain을 순수하게 유지한다.
 */
class ExcludeProblemUseCase
    @Inject
    constructor(
        private val feedbackRepository: ProblemFeedbackRepository,
    ) {
        suspend operator fun invoke(
            problemId: String,
            timestampMillis: Long,
            reason: String? = null,
        ) {
            feedbackRepository.exclude(
                problemId = problemId,
                reason = reason,
                timestampMillis = timestampMillis,
            )
        }
    }
