package com.ddakpul.math.domain.repository

import com.ddakpul.math.domain.model.Entitlement
import kotlinx.coroutines.flow.Flow

/** 프리미엄 이용권 상태의 저장소 — 온디바이스에 기간(만료 시각)만 보관한다. */
interface EntitlementRepository {
    fun observeEntitlement(): Flow<Entitlement>

    suspend fun getEntitlement(): Entitlement

    /**
     * 기간제 이용권을 부여한다. 이미 유효한 이용권이 있으면 남은 기간에 이어 붙인다(스택).
     * 실결제(Play Billing) 검증 성공 시, 또는 테스트 활성화 시 호출된다.
     */
    suspend fun grantPass(
        durationDays: Int,
        nowMillis: Long,
    )
}
