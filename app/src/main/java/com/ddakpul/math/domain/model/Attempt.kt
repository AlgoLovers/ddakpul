package com.ddakpul.math.domain.model

/** 한 번의 풀이 시도 기록. 추천과 리포트의 입력이 된다. */
data class Attempt(
    val problemId: String,
    val isCorrect: Boolean,
    val timeSpentSec: Int,
    val timestamp: Long,
)
