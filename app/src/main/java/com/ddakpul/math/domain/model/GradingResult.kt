package com.ddakpul.math.domain.model

/** 채점 결과. 오답이면서 알려진 흔한 오답이면 [mistake]에 맞춤 오개념 피드백이 담긴다. */
data class GradingResult(
    val problem: Problem,
    val selectedIndex: Int,
    val correctIndex: Int,
    val isCorrect: Boolean,
    val mistake: Mistake?,
    val explanation: String?,
)
