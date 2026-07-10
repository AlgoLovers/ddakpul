package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.repository.LearnerRepository
import javax.inject.Inject

/** 모든 학습 기록과 난이도를 처음 상태로 되돌린다. */
class ResetProgressUseCase
    @Inject
    constructor(
        private val learnerRepository: LearnerRepository,
    ) {
        suspend operator fun invoke() = learnerRepository.resetProgress()
    }
