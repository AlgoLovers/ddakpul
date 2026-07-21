package com.ddakpul.math.domain.model

/**
 * 추천 단위. 유사한 개념·난이도의 문제 묶음이다. 추천 알고리즘은 목표 난이도에 해당하는
 * 그룹을 고른 뒤, 그 안에서 최근에 풀지 않은 문제를 랜덤으로 낸다.
 */
data class ProblemGroup(
    val id: String,
    val area: MathArea,
    val difficulty: Int,
    val conceptTags: List<String>,
    val problems: List<Problem>,
)

/** 그룹들의 모든 문제를 id로 색인 — 추천·통계·능력추정이 공유하는 관용구. */
fun List<ProblemGroup>.problemsById(): Map<String, Problem> = flatMap { it.problems }.associateBy { it.id }
