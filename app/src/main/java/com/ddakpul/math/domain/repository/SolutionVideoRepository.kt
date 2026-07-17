package com.ddakpul.math.domain.repository

import com.ddakpul.math.domain.model.SolutionVideo

/** 방법코드(AA-BB-CC) → 해설 영상 조회. 구현체는 매니페스트(videos.json)를 읽는다. */
interface SolutionVideoRepository {
    /** [methodCode]에 준비된 해설 영상이 있으면 반환, 없으면 null. */
    suspend fun videoForMethod(methodCode: String?): SolutionVideo?
}
