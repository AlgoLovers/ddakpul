package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.repository.OnboardingRepository
import javax.inject.Inject

/** 온보딩을 마치며 아이에게 맞춘 시작 난이도와 하루 목표를 저장하고 완료로 표시한다. */
class CompleteOnboardingUseCase
    @Inject
    constructor(
        private val onboardingRepository: OnboardingRepository,
    ) {
        suspend operator fun invoke(
            startingDifficulty: Int,
            dailyGoal: Int,
        ) {
            onboardingRepository.completeOnboarding(startingDifficulty, dailyGoal)
        }
    }
