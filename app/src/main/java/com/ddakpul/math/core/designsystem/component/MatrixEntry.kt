package com.ddakpul.math.core.designsystem.component

/** [MasteryMatrix]의 한 칸 — [accuracy]가 null이면 시도 없음. */
data class MatrixEntry(
    val solved: Int,
    val accuracy: Float?,
    val emphasized: Boolean = false,
)
