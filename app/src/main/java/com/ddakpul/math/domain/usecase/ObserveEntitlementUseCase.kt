package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.model.Entitlement
import com.ddakpul.math.domain.repository.EntitlementRepository
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject

/** 현재 이용권 상태를 관찰한다 — 페이월/설정에서 무료·프리미엄 표시에 쓴다. */
class ObserveEntitlementUseCase
    @Inject
    constructor(
        private val entitlementRepository: EntitlementRepository,
    ) {
        operator fun invoke(): Flow<Entitlement> = entitlementRepository.observeEntitlement()
    }
