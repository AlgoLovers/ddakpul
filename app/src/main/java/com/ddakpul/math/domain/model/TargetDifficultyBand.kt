package com.ddakpul.math.domain.model

/**
 * 85% 규칙 선택 밴드 — 학습자 θ에서 기대정답률이 목표(~85%)에 가장 가까운 난이도와,
 * 허용 오차 안에 드는 난이도 구간([minDifficulty]..[maxDifficulty], 항상 target을 포함).
 *
 * 문항 선택 시 target 난이도 그룹을 우선하되, 그룹이 비었으면 밴드 안에서 폴백하라는 뜻이다.
 * 모든 값은 [Difficulty.MIN]..[Difficulty.MAX]로 clamp되어 있다.
 *
 * 근거: Wilson et al. 2019 (Nature Comms 10:4646) — 정답률 ~85%에서 학습 속도 최대.
 */
data class TargetDifficultyBand(
    val targetDifficulty: Int,
    val minDifficulty: Int,
    val maxDifficulty: Int,
)
