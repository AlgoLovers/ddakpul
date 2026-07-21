package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.repository.LearnerRepository
import javax.inject.Inject

/** 상위 난이도(기본 상한 위) 열기 설정을 저장한다. 켜면 추천에 모든 난이도가 나온다. */
class SetUnlockAllLevelsUseCase
    @Inject
    constructor(
        private val learnerRepository: LearnerRepository,
    ) {
        suspend operator fun invoke(enabled: Boolean) = learnerRepository.setUnlockAllLevels(enabled)
    }
