package com.ddakpul.math.domain.model

/** 한 번의 풀이 시도 기록. 추천과 리포트의 입력이 된다. */
data class Attempt(
    val problemId: String,
    val isCorrect: Boolean,
    val timeSpentSec: Int,
    val timestamp: Long,
    /**
     * 오답 노트에서 다시 푼 '복습' 시도인지. 복습 재풀이는 추천 규칙(연속 정답·오답 스트릭)의
     * 입력에서 제외해 난이도 승급/강등을 흔들지 않는다 — 통계·오답 노트에는 그대로 반영된다.
     */
    val reviewMode: Boolean = false,
) {
    companion object {
        /**
         * 시도 시간 기록 상한(30분). 문제를 열어둔 채 기기가 잠들면 경과 시간이 통째로
         * 기록돼 평균 시간 통계를 왜곡한다 — 기록 시점과 집계 시점(과거 데이터) 모두 이 값으로 clamp.
         */
        const val MAX_TIME_SPENT_SEC: Int = 1_800
    }
}
