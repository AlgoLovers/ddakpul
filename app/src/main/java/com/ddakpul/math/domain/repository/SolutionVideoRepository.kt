package com.ddakpul.math.domain.repository

import com.ddakpul.math.domain.model.SolutionVideo

/**
 * 방법코드(AA-BB-CC) → 해설 영상 조회·확보.
 * 매니페스트는 원격(신규 영상이 앱 업데이트 없이 추가되도록)을 우선하고, 오프라인이면
 * 마지막으로 받아 둔 사본 → 앱 내장 시드 순으로 폴백한다.
 */
interface SolutionVideoRepository {
    /** [methodCode]에 준비된 해설 영상이 있으면 반환, 없으면 null. */
    suspend fun videoForMethod(methodCode: String?): SolutionVideo?

    /** 이 영상(정확히 이 버전)이 로컬에 캐시돼 있는가. */
    fun isCached(video: SolutionVideo): Boolean

    /**
     * 재생 가능한 로컬 파일 경로를 확보한다 — 캐시돼 있으면 즉시, 아니면 내려받는다
     * (완결성 검증 포함, 같은 방법의 옛 버전 캐시는 삭제). 실패 시 예외 대신 null.
     */
    suspend fun ensureLocal(
        video: SolutionVideo,
        onProgress: (received: Long, total: Long) -> Unit,
    ): String?
}
