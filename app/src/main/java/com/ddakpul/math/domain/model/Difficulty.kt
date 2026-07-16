package com.ddakpul.math.domain.model

/** 난이도 범위와 clamp 규칙(추천 규칙 6). 매직값을 흩뿌리지 않도록 한곳에 모은다. */
object Difficulty {
    const val MIN = 1

    /**
     * 최상위 난이도. 학년이 아니라 '사고력 난이도 폭'이라, 초등 입문(1)부터 경시·올림피아드·대학/성인
     * 수준(상위)까지 한 축으로 이어진다. 천장을 차근차근 올려 전 연령을 담는다(현재 10: 올림피아드·대학 심화까지).
     */
    const val MAX = 10

    /** 학습 기록이 없을 때 시작 난이도 — 너무 쉽지도 어렵지도 않은 중하 지점. */
    const val DEFAULT = 2

    /** 난이도를 [MIN]~[MAX]로 고정한다. */
    fun clamp(value: Int): Int = value.coerceIn(MIN, MAX)
}
