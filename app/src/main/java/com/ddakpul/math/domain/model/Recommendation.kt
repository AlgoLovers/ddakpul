package com.ddakpul.math.domain.model

/** 추천이 내려진 근거. 각 값이 CLAUDE.md 추천 규칙과 1:1로 대응하며, 테스트로 검증한다. */
enum class RecommendationReason {
    START, // 첫 문제(기록 없음)
    ADVANCED, // 규칙1: 연속 정답 → 난이도 상승
    RETREATED, // 규칙2: 연속 오답 → 난이도 하강
    STAY, // 규칙3: 혼조 → 같은 난이도 유지
    REMEDIATION, // 규칙4: 정체 감지 → 해설 제공 + 선수 개념 복귀
}

/** 추천 결과 — 다음에 낼 문제와 그 근거. */
data class Recommendation(
    val problem: Problem,
    val group: ProblemGroup,
    val targetDifficulty: Int,
    val reason: RecommendationReason,
    val showExplanation: Boolean,
)
