package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.repository.LearnerRepository
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject

/** 아이가 스스로 정한 하루 목표 문항 수 스트림. */
class ObserveDailyGoalUseCase
    @Inject
    constructor(
        private val learnerRepository: LearnerRepository,
    ) {
        operator fun invoke(): Flow<Int> = learnerRepository.observeDailyGoal()
    }
