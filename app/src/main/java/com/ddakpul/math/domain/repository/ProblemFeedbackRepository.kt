package com.ddakpul.math.domain.repository

import com.ddakpul.math.domain.model.ExcludedProblem
import kotlinx.coroutines.flow.Flow

/** 문제에 대한 사용자 피드백(제외 표시) 저장소. */
interface ProblemFeedbackRepository {
    suspend fun exclude(
        problemId: String,
        reason: String?,
        timestampMillis: Long,
    )

    /** 추천·학습지에서 걸러낼 제외 문제 ID 집합. */
    suspend fun getExcludedIds(): Set<String>

    /** 내보내기용 전체 제외 목록(제외 시각 오름차순). */
    suspend fun getAllExclusions(): List<ExcludedProblem>

    /** 설정 화면에 보여줄 제외 문제 수 스트림. */
    fun observeExcludedCount(): Flow<Int>
}
