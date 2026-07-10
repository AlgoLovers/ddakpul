package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.repository.ProblemFeedbackRepository
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject

/** 제외한 문제 수 스트림 — 설정 화면의 내보내기 버튼 상태에 쓴다. */
class ObserveExcludedCountUseCase
    @Inject
    constructor(
        private val feedbackRepository: ProblemFeedbackRepository,
    ) {
        operator fun invoke(): Flow<Int> = feedbackRepository.observeExcludedCount()
    }
