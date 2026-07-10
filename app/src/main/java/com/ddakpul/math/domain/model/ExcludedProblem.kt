package com.ddakpul.math.domain.model

/**
 * 아이가 "별로예요"로 제외한 문제. 추천·학습지에서 다시 나오지 않으며,
 * 목록을 내보내 문제은행 개선(다음 업데이트에서 삭제·교체)의 입력으로 쓴다.
 */
data class ExcludedProblem(
    val problemId: String,
    val reason: String?,
    val excludedAtMillis: Long,
)
