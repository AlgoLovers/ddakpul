package com.ddakpul.math.domain.model

/** 영역별 풀이 통계. */
data class AreaStat(
    val area: MathArea,
    val solved: Int,
    val correct: Int,
) {
    val accuracy: Float get() = if (solved == 0) 0f else correct.toFloat() / solved
}

/** 부모용 리포트 데이터. 학습 기록으로부터 파생된다. */
data class LearnerReport(
    val totalSolved: Int,
    val correctCount: Int,
    val currentDifficulty: Int,
    val areaStats: List<AreaStat>,
) {
    val accuracy: Float get() = if (totalSolved == 0) 0f else correctCount.toFloat() / totalSolved
    val isEmpty: Boolean get() = totalSolved == 0
}
