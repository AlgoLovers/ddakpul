package com.ddakpul.math.domain.model

/**
 * 오답 노트 한 항목 — '가장 최근 시도가 오답'인 문제 하나.
 * 다시 풀어서 맞히면(가장 최근 시도가 정답이 되면) 목록에서 빠진다(오답 졸업).
 */
data class WrongProblem(
    val problem: Problem,
    /** 이 문제를 마지막으로 틀린 시각 — 오답 노트의 날짜·정렬 기준. */
    val lastWrongAt: Long,
    /** 지금까지 이 문제를 틀린 횟수. */
    val wrongCount: Int,
)
