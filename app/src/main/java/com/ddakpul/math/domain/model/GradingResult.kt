package com.ddakpul.math.domain.model

/** 채점 결과. 오답이면서 알려진 흔한 오답이면 [mistake]에 맞춤 오개념 피드백이 담긴다. */
data class GradingResult(
    val problem: Problem,
    val selectedIndex: Int,
    val correctIndex: Int,
    val isCorrect: Boolean,
    val mistake: Mistake?,
    val explanation: String?,
    /** 2차(심화) 풀이 — 이용권 전용. 결과 화면이 무료/유료에 맞게 노출한다. */
    val detailedExplanation: String? = null,
)
