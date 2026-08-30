package com.ddakpul.math.domain.time

/**
 * 테스트용 고정 시계. [nowMillis]를 직접 옮겨 "문항을 30분 넘게 열어둔" 같은 상황을
 * 실제로 기다리지 않고 재현한다.
 */
class FakeClock(
    var now: Long = 0L,
    private val offsetMillis: Long = 0L,
) : Clock {
    override fun nowMillis(): Long = now

    override fun zoneOffsetMillis(): Long = offsetMillis

    /** 시계를 [millis]만큼 앞으로 돌린다. */
    fun advance(millis: Long) {
        now += millis
    }
}
