package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.model.PremiumPass
import com.ddakpul.math.domain.repository.EntitlementRepository
import javax.inject.Inject

/**
 * 이용권 기간을 활성화한다. 지금은 로컬 활성화(테스트) 진입점이며, 실결제(Play Billing)를
 * 붙이면 결제 검증 성공 콜백이 이 UseCase를 호출하도록 바꾼다.
 */
class ActivatePassUseCase
    @Inject
    constructor(
        private val entitlementRepository: EntitlementRepository,
    ) {
        suspend operator fun invoke(
            pass: PremiumPass,
            nowMillis: Long,
        ) {
            entitlementRepository.grantPass(pass.durationDays, nowMillis)
        }
    }
