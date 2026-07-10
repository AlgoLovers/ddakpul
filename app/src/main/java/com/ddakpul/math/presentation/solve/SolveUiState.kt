package com.ddakpul.math.presentation.solve

import com.ddakpul.math.domain.model.GradingResult
import com.ddakpul.math.domain.model.MathArea
import com.ddakpul.math.domain.model.Problem
import com.ddakpul.math.domain.model.RecommendationReason
import com.ddakpul.math.domain.model.SessionGoals

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
    /** 오늘 푼 문제 수 — 오늘의 목표 진행바에 쓴다. */
    val todaySolved: Int = 0,
    val dailyGoal: Int = SessionGoals.DAILY_GOAL_PROBLEMS,
    /** 이번 세션에서 이어지고 있는 연속 정답 수 — 연속 정답 칭찬의 기준. */
    val sessionStreak: Int = 0,
) {
    val canSubmit: Boolean get() = phase == SolvePhase.SOLVING && selectedIndex != null
}
