package com.ddakpul.math.domain.model

/** 프리미엄 이용권 상태. [premiumUntilMillis](포함 이전)까지 유효하며, 0이면 무료다. */
data class Entitlement(
    val premiumUntilMillis: Long = 0L,
) {
    /** 구매한 이용권이 유효한가. */
    fun isPremium(nowMillis: Long): Boolean = nowMillis < premiumUntilMillis

    /**
     * 실제 전체 개방 여부 = 구매한 이용권이 유효하거나, 출시 기념 무료 기간 중.
     * 콘텐츠·리포트 접근 게이트는 이 값을 쓴다(무료 프로모션 동안 모두 열린다).
     */
    fun hasFullAccess(nowMillis: Long): Boolean = isPremium(nowMillis) || Monetization.isLaunchFree(nowMillis)
}

/**
 * 판매하는 이용권 종류 — 자동갱신 없는 기간제(만료되면 그냥 끝, 원하면 재구매).
 * [defaultPriceLabel]은 표시용 기본값이고 실제 가격은 스토어에서 받아 대체한다.
 * [productId]는 Play Console 인앱 상품 ID와 1:1로 맞춘다.
 */
enum class PremiumPass(
    val durationDays: Int,
    val defaultPriceLabel: String,
    val productId: String,
) {
    SIX_MONTHS(durationDays = 182, defaultPriceLabel = "₩9,900", productId = "ddakpul_pass_6m"),
    ONE_YEAR(durationDays = 365, defaultPriceLabel = "₩19,000", productId = "ddakpul_pass_1y"),
}

/** 수익화 경계 상수. */
object Monetization {
    /** 무료로 풀 수 있는 최고 난이도 — 이보다 높은 난이도는 이용권이 필요하다. */
    const val FREE_MAX_DIFFICULTY = 3

    /**
     * 출시 기념 전면 무료 마감 시각(epoch millis). 이 시각 이전에는 난이도 4~7·전체 리포트가
     * 이용권 없이 모두 무료다. 기본값 = KST 2026-11-01 00:00(= 2026-10-31 자정까지 무료).
     * ⚠️ 실제 출시 일정에 맞춰 조정할 것. 0으로 두면 프로모션 없음(원래 무료/유료 경계).
     */
    const val LAUNCH_FREE_UNTIL_MILLIS = 1_793_458_800_000L

    /** 지금이 출시 기념 무료 기간인가. */
    fun isLaunchFree(nowMillis: Long): Boolean = LAUNCH_FREE_UNTIL_MILLIS > 0L && nowMillis < LAUNCH_FREE_UNTIL_MILLIS
}
