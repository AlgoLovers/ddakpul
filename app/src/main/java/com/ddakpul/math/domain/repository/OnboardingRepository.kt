package com.ddakpul.math.domain.repository

import kotlinx.coroutines.flow.Flow

/** 첫 실행 온보딩 상태의 저장소 — 학습 진행과 분리된, 앱 최초 실행 관심사. */
interface OnboardingRepository {
    /** 온보딩(소개·하루 목표·시작 난이도)을 마쳤는지 스트림. */
    fun observeOnboardingComplete(): Flow<Boolean>

    /** 온보딩을 마치며 시작 난이도와 하루 목표를 저장하고 완료로 표시한다. */
    suspend fun completeOnboarding(
        startingDifficulty: Int,
        dailyGoal: Int,
    )
}
