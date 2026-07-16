package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.repository.OnboardingRepository
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject

/** 첫 실행 온보딩을 이미 마쳤는지 관찰한다 — 앱 진입 시 온보딩/본화면 분기의 입력. */
class ObserveOnboardingCompleteUseCase
    @Inject
    constructor(
        private val onboardingRepository: OnboardingRepository,
    ) {
        operator fun invoke(): Flow<Boolean> = onboardingRepository.observeOnboardingComplete()
    }
