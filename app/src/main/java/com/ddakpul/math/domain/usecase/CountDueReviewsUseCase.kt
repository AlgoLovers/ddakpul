package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.repository.LearnerRepository
import javax.inject.Inject

/**
 * 오늘 복습이 만기된 그룹 수 — 홈의 복습 카드가 "복습할 문제 N개"를 보여줄 때 쓴다.
 * [GetNextProblemUseCase]와 같은 큐([ComputeReviewQueueUseCase])를 읽되 상태는 바꾸지 않는다(read-only).
 */
class CountDueReviewsUseCase
    @Inject
    constructor(
        private val getActiveGroups: GetActiveProblemGroupsUseCase,
        private val learnerRepository: LearnerRepository,
        private val computeReviewQueue: ComputeReviewQueueUseCase,
    ) {
        suspend operator fun invoke(
            zoneOffsetMillis: Long,
            nowMillis: Long,
        ): Int {
            val groups = getActiveGroups()
            if (groups.isEmpty()) return 0
            val attempts = learnerRepository.getAllAttempts()
            return computeReviewQueue(
                attempts = attempts,
                groups = groups,
                zoneOffsetMillis = zoneOffsetMillis,
                nowMillis = nowMillis,
            ).size
        }
    }
