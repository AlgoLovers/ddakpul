package com.ddakpul.math.data.time

import com.ddakpul.math.domain.time.Clock
import java.util.TimeZone
import javax.inject.Inject
import javax.inject.Singleton

/** 기기 시계에 붙는 기본 [Clock] 구현. 앱 전역에서 한 인스턴스면 충분하다. */
@Singleton
class SystemClock
    @Inject
    constructor() : Clock {
        override fun nowMillis(): Long = System.currentTimeMillis()

        override fun zoneOffsetMillis(): Long = TimeZone.getDefault().getOffset(nowMillis()).toLong()
    }
