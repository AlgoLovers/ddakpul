package com.ddakpul.math.domain.model

/**
 * 추천 알고리즘의 입력이 되는 학습자 상태.
 *
 * [recentAttempts]는 **오래된 것 → 최신 순(시간 오름차순)**으로 정렬돼 있다고 가정한다
 * (리스트의 마지막 원소가 가장 최근 시도). 연속 정답/오답 판정이 이 순서에 의존한다.
 */
data class LearnerState(
    val currentDifficulty: Int,
    val areaMastery: Map<MathArea, Float>,
    val recentAttempts: List<Attempt>,
)
