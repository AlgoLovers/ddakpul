package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.repository.LearnerRepository
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject

/** 상위 난이도(기본 상한 위) 열기 설정 스트림 — 설정 스위치 표시용. */
class ObserveUnlockAllLevelsUseCase
    @Inject
    constructor(
        private val learnerRepository: LearnerRepository,
    ) {
        operator fun invoke(): Flow<Boolean> = learnerRepository.observeUnlockAllLevels()
    }
