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
}
