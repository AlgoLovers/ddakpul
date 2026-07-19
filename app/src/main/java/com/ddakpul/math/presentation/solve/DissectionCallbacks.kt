package com.ddakpul.math.presentation.solve

import com.ddakpul.math.domain.model.Cell

/** 등분 퍼즐 조작 콜백 묶음 — SolveContent 파라미터 폭증을 막는다. */
data class DissectionCallbacks(
    val onTap: (Cell) -> Unit,
    val onSelectPiece: (Int) -> Unit,
    val onClear: () -> Unit,
    val onSubmit: () -> Unit,
)
