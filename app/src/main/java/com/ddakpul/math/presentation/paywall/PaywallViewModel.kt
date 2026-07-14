package com.ddakpul.math.presentation.paywall

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.ddakpul.math.domain.model.Entitlement
import com.ddakpul.math.domain.model.Monetization
import com.ddakpul.math.domain.model.PremiumPass
import com.ddakpul.math.domain.usecase.ActivatePassUseCase
import com.ddakpul.math.domain.usecase.ObserveEntitlementUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import javax.inject.Inject

/** 페이월 상태(현재 이용권)와 이용권 활성화를 관장한다. */
@HiltViewModel
class PaywallViewModel
    @Inject
    constructor(
        observeEntitlement: ObserveEntitlementUseCase,
        private val activatePass: ActivatePassUseCase,
    ) : ViewModel() {
        val entitlement: StateFlow<Entitlement> =
            observeEntitlement()
                .stateIn(viewModelScope, SharingStarted.WhileSubscribed(STOP_TIMEOUT_MILLIS), Entitlement())

        /** 출시 기념 무료 마감 시각(프로모션 중이면 > 0) — 지금은 결제 안 해도 다 열려 있다는 안내용. */
        val launchFreeUntilMillis: Long =
            Monetization.LAUNCH_FREE_UNTIL_MILLIS.takeIf { Monetization.isLaunchFree(System.currentTimeMillis()) } ?: 0L

        fun activate(pass: PremiumPass) {
            viewModelScope.launch {
                activatePass(pass, System.currentTimeMillis())
            }
        }

        private companion object {
            const val STOP_TIMEOUT_MILLIS = 5_000L
        }
    }
