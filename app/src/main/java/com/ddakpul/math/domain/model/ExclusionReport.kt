package com.ddakpul.math.domain.model

/**
 * 제외("별로예요")한 문제 목록의 구조화 결과. domain은 표시 언어·형식을 모른다 —
 * 사람이 읽을 공유 텍스트로 바꾸는 일은 presentation이 문자열 리소스로 처리한다.
 */
data class ExclusionReport(
    val count: Int,
    val entries: List<Entry>,
) {
    data class Entry(
        /** 목록 순번(1부터). */
        val order: Int,
        val problemId: String,
        /** 문제은행에서 이미 사라진 문제면 null. */
        val area: MathArea?,
        /** 사라진 문제면 null. */
        val difficulty: Int?,
        /** 지문 미리보기. 사라진 문제면 빈 문자열. */
        val statementPreview: String,
        val reason: String?,
    )
}
