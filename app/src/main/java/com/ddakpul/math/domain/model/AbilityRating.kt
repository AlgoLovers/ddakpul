package com.ddakpul.math.domain.model

/**
 * 한 영역([MathArea])에 대한 학습자 능력 추정치 — Elo-lite 엔진의 θ.
 *
 * [rating]은 문항 레이팅 b와 같은 정수 척도 위의 값이고(레이팅차가 기대정답률을 결정),
 * [attemptCount]는 그 영역의 누적 시도 수로 K 감쇠(추정 신뢰도의 정수 근사)의 입력이 된다.
 * 이 값은 저장되지 않는다 — 전체 시도 기록을 replay해서 매번 복원한다(마이그레이션 프리).
 *
 * 근거: Pelánek 2016 (Elo in adaptive educational systems), docs/CONTENT_ENGINE_STRATEGY.md §2.1.
 */
data class AbilityRating(
    val rating: Int,
    val attemptCount: Int,
)
