package com.ddakpul.math.domain.model

/** 프리미엄 이용권 상태. [premiumUntilMillis](포함 이전)까지 유효하며, 0이면 무료다. */
data class Entitlement(
    val premiumUntilMillis: Long = 0L,
) {
    fun isPremium(nowMillis: Long): Boolean = nowMillis < premiumUntilMillis
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
}
