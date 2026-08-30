package com.ddakpul.math.domain.time

/**
 * 현재 시각의 공급자. `System.currentTimeMillis()`를 직접 부르는 코드는 그 순간의 기기 시계에
 * 묶여 단위 테스트가 불가능해진다 — 시간이 필요한 곳은 이 인터페이스에만 의존하고,
 * 테스트는 고정 시각 구현을 넣는다.
 *
 * domain 계층 소속 — 순수 Kotlin. 구현([com.ddakpul.math.data.time.SystemClock])은 data에 둔다.
 */
interface Clock {
    /** epoch 밀리초 기준 현재 시각. */
    fun nowMillis(): Long

    /**
     * 지금 이 순간의 로컬 타임존 오프셋(ms). '오늘'을 로컬 자정 기준으로 가르는 데 쓴다 —
     * 호출 시점마다 다시 읽으므로 서머타임·타임존 변경을 따라간다.
     */
    fun zoneOffsetMillis(): Long
}
