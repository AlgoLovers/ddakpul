package com.ddakpul.math.domain.model

import com.google.common.truth.Truth.assertThat
import org.junit.Test

class EntitlementTest {
    @Test
    fun free_whenNoPass() {
        assertThat(Entitlement(premiumUntilMillis = 0L).isPremium(nowMillis = 1_000L)).isFalse()
    }

    @Test
    fun premium_beforeExpiry() {
        assertThat(Entitlement(premiumUntilMillis = 2_000L).isPremium(nowMillis = 1_000L)).isTrue()
    }

    @Test
    fun expired_atOrAfterExpiry() {
        assertThat(Entitlement(premiumUntilMillis = 1_000L).isPremium(nowMillis = 1_000L)).isFalse()
        assertThat(Entitlement(premiumUntilMillis = 1_000L).isPremium(nowMillis = 1_001L)).isFalse()
    }

    @Test
    fun launchFree_grantsFullAccessEvenWithoutPass() {
        // 미구매(0)라도 프로모션 마감 직전이면 전체 개방.
        val duringPromo = Monetization.LAUNCH_FREE_UNTIL_MILLIS - 1L
        assertThat(Monetization.isLaunchFree(duringPromo)).isTrue()
        assertThat(Entitlement(premiumUntilMillis = 0L).hasFullAccess(duringPromo)).isTrue()
        assertThat(Entitlement(premiumUntilMillis = 0L).isPremium(duringPromo)).isFalse()
    }

    @Test
    fun afterLaunchPromo_freeUserHasNoFullAccess() {
        val afterPromo = Monetization.LAUNCH_FREE_UNTIL_MILLIS
        assertThat(Monetization.isLaunchFree(afterPromo)).isFalse()
        assertThat(Entitlement(premiumUntilMillis = 0L).hasFullAccess(afterPromo)).isFalse()
        // 구매한 이용권이 유효하면 프로모션과 무관하게 전체 개방.
        assertThat(Entitlement(premiumUntilMillis = afterPromo + 1L).hasFullAccess(afterPromo)).isTrue()
    }
}
