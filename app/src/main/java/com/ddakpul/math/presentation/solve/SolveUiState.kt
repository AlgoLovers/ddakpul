package com.ddakpul.math.presentation.solve

import com.ddakpul.math.domain.model.Cell
import com.ddakpul.math.domain.model.GradingResult
import com.ddakpul.math.domain.model.MathArea
import com.ddakpul.math.domain.model.Problem
import com.ddakpul.math.domain.model.RecommendationReason
import com.ddakpul.math.domain.model.SessionGoals
import com.ddakpul.math.domain.model.SolutionVideo
import com.ddakpul.math.domain.usecase.DissectionValidation

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
    /** 오늘 풀이에 쓴 총 시간(초). */
    val todayTimeSpentSec: Int = 0,
    /** 현재 문제의 방법에 준비된 해설 영상(있을 때만 '동영상 풀이 보기' 노출). */
    val solutionVideo: SolutionVideo? = null,
    /** 등분 퍼즐 풀이 상태 — 칸→조각 배정, 선택한 조각색, 채점 결과(4지선다면 무의미). */
    val dissectionAssignment: Map<Cell, Int> = emptyMap(),
    val dissectionPiece: Int = 0,
    val dissectionResult: DissectionValidation? = null,
) {
    /** 구성형(격자 등분) 문제 여부 — 화면·채점 분기용. */
    val isDissection: Boolean get() = problem?.isDissection == true

    val canSubmit: Boolean get() = phase == SolvePhase.SOLVING && selectedIndex != null

    /** 복습 문제 여부 — 화면에 배지로 표시한다. */
    val isReview: Boolean get() = reason == RecommendationReason.REVIEW

    /**
     * 세션 소프트 컷 — 목표를 채웠거나 집중 한계(20분)를 넘겼으면 부드러운 종료를 제안한다.
     * 강제 종료가 아니라 제안이다(자율성 존중).
     */
    val softCutSuggested: Boolean
        get() = todaySolved >= dailyGoal || todayTimeSpentSec >= SessionGoals.SESSION_SOFT_CUT_SEC
}
