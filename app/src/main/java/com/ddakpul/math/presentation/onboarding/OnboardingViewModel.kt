package com.ddakpul.math.presentation.onboarding

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.ddakpul.math.domain.usecase.CompleteOnboardingUseCase
import com.ddakpul.math.domain.usecase.ObserveOnboardingCompleteUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * 앱 진입 시 온보딩/본화면 분기를 관장한다. [onboardingComplete]가 아직 null이면 로딩 중,
 * false면 온보딩, true면 본화면.
 */
@HiltViewModel
class OnboardingViewModel
    @Inject
    constructor(
        observeOnboardingComplete: ObserveOnboardingCompleteUseCase,
        private val completeOnboarding: CompleteOnboardingUseCase,
    ) : ViewModel() {
        /** null = 아직 확인 중, true/false = 온보딩 완료 여부. */
        val onboardingComplete: StateFlow<Boolean?> =
            observeOnboardingComplete()
                .stateIn(viewModelScope, SharingStarted.WhileSubscribed(STOP_TIMEOUT_MILLIS), null)

        fun complete(
            startingDifficulty: Int,
            dailyGoal: Int,
        ) {
            viewModelScope.launch {
                completeOnboarding(startingDifficulty, dailyGoal)
            }
        }

        private companion object {
            const val STOP_TIMEOUT_MILLIS = 5_000L
        }
    }
