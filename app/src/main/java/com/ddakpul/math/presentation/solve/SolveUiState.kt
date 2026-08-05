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
    /** 오답 노트에서 특정 문제를 다시 푸는 복습 모드. 오늘 진행·제외 버튼을 숨기고 '다음' 대신 '오답 노트로'를 보인다. */
    val reviewMode: Boolean = false,
    /** 오늘 푼 문제 수 — 오늘의 목표 진행바에 쓴다. */
    val todaySolved: Int = 0,
    /**
     * 지금 화면의 문제가 오늘 몇 번째인지 — 문제를 받은 순간 고정한다.
     * [todaySolved]로 그리면 채점하는 순간 같은 문제를 보는 채로 번호가 +1 된다(2026-08 QA).
     */
    val problemOrdinal: Int = 1,
    val dailyGoal: Int = SessionGoals.DAILY_GOAL_PROBLEMS,
    /** 이번 세션에서 이어지고 있는 연속 정답 수 — 연속 정답 칭찬의 기준. */
    val sessionStreak: Int = 0,
    /**
     * 오답 직후 규칙 7(같은 그룹 다른 문제 재도전)이 이어질 가능성이 높은지 —
     * 채점 시트의 CTA 문구("비슷한 문제 한 번 더")에 쓴다. 세션 내 직전 정답 뒤 첫 오답일 때만
     * true(확실한 신호만). 정체 누적 등으로 다른 규칙이 앞설 수 있어 '가능성'이다.
     */
    val retryLikely: Boolean = false,
    /** 이번 채점으로 하루 목표를 막 채웠는지 — 축하는 그 한 번만 띄운다. */
    val goalJustReached: Boolean = false,
    /** 오늘 풀이에 쓴 총 시간(초). 통계 표시용 — 소프트 컷 판정에는 쓰지 않는다. */
    val todayTimeSpentSec: Int = 0,
    /** 이번 화면 세션(앱을 열고 문제풀기에 들어온 뒤) 경과 시간(초). */
    val sessionElapsedSec: Int = 0,
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
     *
     * 시간 기준은 반드시 **이번 세션 경과**다 — '오늘 누적'으로 재면 아침에 20분 푼 아이가
     * 저녁에 첫 문제를 풀자마자 "오늘은 여기까지"를 보게 된다(2026-08 QA).
     */
    val softCutSuggested: Boolean
        get() = todaySolved >= dailyGoal || sessionElapsedSec >= SessionGoals.SESSION_SOFT_CUT_SEC
}
