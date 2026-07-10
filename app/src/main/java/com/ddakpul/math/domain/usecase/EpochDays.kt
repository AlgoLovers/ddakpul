package com.ddakpul.math.domain.usecase

internal const val MILLIS_PER_DAY = 86_400_000L

/**
 * 로컬 자정 기준 경과 일수. 타임존 오프셋을 더한 뒤 하루(ms)로 나누므로
 * 같은 날 밤 11시와 아침 7시가 같은 값이 된다. 통계·복습 스케줄이 공유한다.
 */
internal fun epochDay(
    timestamp: Long,
    zoneOffsetMillis: Long,
): Long = Math.floorDiv(timestamp + zoneOffsetMillis, MILLIS_PER_DAY)
