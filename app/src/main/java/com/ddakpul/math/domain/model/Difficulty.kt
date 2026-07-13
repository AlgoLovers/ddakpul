package com.ddakpul.math.domain.model

/** 난이도 범위와 clamp 규칙(추천 규칙 6). 매직값을 흩뿌리지 않도록 한곳에 모은다. */
object Difficulty {
    const val MIN = 1

    /** 최상위 난이도. 5까지도 쉬운 아이를 위해 6·7(경시·올림피아드급)까지 둔다. 학년이 아니라 난이도 폭이다. */
    const val MAX = 7

    /** 학습 기록이 없을 때 시작 난이도 — 너무 쉽지도 어렵지도 않은 중하 지점. */
    const val DEFAULT = 2

    /** 난이도를 [MIN]~[MAX]로 고정한다. */
    fun clamp(value: Int): Int = value.coerceIn(MIN, MAX)
}
