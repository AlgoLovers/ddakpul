package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.model.SessionGoals
import com.ddakpul.math.domain.repository.LearnerRepository
import javax.inject.Inject

/** 하루 목표를 저장한다. 허용된 선택지 밖의 값은 가장 가까운 선택지로 맞춘다. */
class SetDailyGoalUseCase
    @Inject
    constructor(
        private val learnerRepository: LearnerRepository,
    ) {
        suspend operator fun invoke(goal: Int) {
            val safeGoal = SessionGoals.GOAL_OPTIONS.minByOrNull { kotlin.math.abs(it - goal) } ?: SessionGoals.DAILY_GOAL_PROBLEMS
            learnerRepository.setDailyGoal(safeGoal)
        }
    }
