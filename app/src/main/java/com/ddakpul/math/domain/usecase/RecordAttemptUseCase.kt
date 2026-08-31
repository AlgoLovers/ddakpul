package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.model.Attempt
import com.ddakpul.math.domain.model.Problem
import com.ddakpul.math.domain.repository.LearnerRepository
import javax.inject.Inject

/**
 * 한 번의 풀이 시도를 기록한다 — 4지선다·구성형·"모르겠어요" 세 경로가 공유하는 단 하나의 입구.
 *
 * 기록 시간은 여기서 [Attempt.MAX_TIME_SPENT_SEC]로 clamp한다. 문제를 열어둔 채 기기가 잠들면
 * 경과 시간이 통째로 들어와 평균 시간 통계를 영구히 왜곡하는데, 이 불변식을 화면 쪽에 맡기면
 * 새 풀이 경로가 생길 때마다 조용히 빠질 수 있다.
 */
class RecordAttemptUseCase
    @Inject
    constructor(
        private val learnerRepository: LearnerRepository,
    ) {
        suspend operator fun invoke(
            problem: Problem,
            isCorrect: Boolean,
            timeSpentSec: Int,
            timestamp: Long,
            reviewMode: Boolean,
        ) {
            learnerRepository.recordAttempt(
                Attempt(
                    problemId = problem.id,
                    isCorrect = isCorrect,
                    timeSpentSec = timeSpentSec.coerceIn(0, Attempt.MAX_TIME_SPENT_SEC),
                    timestamp = timestamp,
                    reviewMode = reviewMode,
                ),
            )
        }
    }
