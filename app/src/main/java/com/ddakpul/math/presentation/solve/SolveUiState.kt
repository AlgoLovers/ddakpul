package com.ddakpul.math.presentation.solve

import com.ddakpul.math.domain.model.GradingResult
import com.ddakpul.math.domain.model.MathArea
import com.ddakpul.math.domain.model.Problem
import com.ddakpul.math.domain.model.RecommendationReason

/** 문제 풀이 화면의 진행 단계. */
enum class SolvePhase { LOADING, SOLVING, GRADED, EMPTY }

/** 문제 풀이 화면의 단일 불변 상태. */
data class SolveUiState(
    val phase: SolvePhase = SolvePhase.LOADING,
    val problem: Problem? = null,
    val area: MathArea? = null,
    val difficulty: Int = 0,
    val selectedIndex: Int? = null,
    val result: GradingResult? = null,
    val showExplanation: Boolean = false,
    val reason: RecommendationReason? = null,
) {
    val canSubmit: Boolean get() = phase == SolvePhase.SOLVING && selectedIndex != null
}
