package com.ddakpul.math.core.designsystem.component

/** [MiniBarChart]의 막대 하나 — [emphasized]는 "오늘"처럼 강조할 칸. */
data class BarEntry(
    val value: Float,
    val emphasized: Boolean = false,
)
