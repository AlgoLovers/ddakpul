package com.ddakpul.math.presentation.common

import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/**
 * 출시 기념 무료 마감일을 'yyyy.M.d'로 포맷한다. [untilMillis]는 무료가 끝나는 시각(그 직전까지 무료)이라
 * 마지막 무료일을 보이려고 1ms 빼서 표시한다. 예: 2026-11-01 00:00 → "2026.10.31".
 */
fun launchFreeDeadlineText(untilMillis: Long): String = SimpleDateFormat("yyyy.M.d", Locale.KOREA).format(Date(untilMillis - 1))
