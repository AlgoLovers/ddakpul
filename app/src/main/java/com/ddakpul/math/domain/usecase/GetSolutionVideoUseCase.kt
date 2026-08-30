package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.model.SolutionVideo
import com.ddakpul.math.domain.repository.SolutionVideoRepository
import javax.inject.Inject

/**
 * 방법코드에 준비된 해설 영상을 찾는다. 없거나 조회에 실패하면(오프라인 등) null —
 * 영상은 부가 기능이라 실패가 풀이 흐름을 막아서는 안 된다.
 */
class GetSolutionVideoUseCase
    @Inject
    constructor(
        private val repository: SolutionVideoRepository,
    ) {
        suspend operator fun invoke(methodCode: String?): SolutionVideo? {
            if (methodCode == null) return null
            return runCatching { repository.videoForMethod(methodCode) }.getOrNull()
        }
    }
