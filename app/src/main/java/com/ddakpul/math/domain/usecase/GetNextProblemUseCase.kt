package com.ddakpul.math.domain.usecase

import com.ddakpul.math.core.common.AppError
import com.ddakpul.math.core.common.AppResult
import com.ddakpul.math.domain.model.Recommendation
import com.ddakpul.math.domain.repository.LearnerRepository
import javax.inject.Inject

/**
 * 저장소에서 문제은행·학습자 상태·복습 만기 목록을 모아 [RecommendNextProblemUseCase]로
 * 다음 문제를 정하고, 난이도가 바뀌었으면 진행 상태에 반영한다. ViewModel은 이 UseCase만 호출한다.
 * 문제은행은 [GetActiveProblemGroupsUseCase]를 거치므로 "별로예요"로 제외한 문제는 나오지 않는다.
 *
 * 시간([nowMillis]·[zoneOffsetMillis])과 오늘 푼 수([todaySolved])는 호출부가 주입해
 * domain을 순수하게 유지한다.
 */
class GetNextProblemUseCase
    @Inject
    constructor(
        private val getActiveGroups: GetActiveProblemGroupsUseCase,
        private val learnerRepository: LearnerRepository,
        private val recommend: RecommendNextProblemUseCase,
        private val computeReviewQueue: ComputeReviewQueueUseCase,
    ) {
        suspend operator fun invoke(
            todaySolved: Int,
            zoneOffsetMillis: Long,
            nowMillis: Long,
        ): AppResult<Recommendation> {
            val groups = getActiveGroups()
            if (groups.isEmpty()) return AppResult.Failure(AppError.EmptyProblemBank)

            val state = learnerRepository.getLearnerState()
            val reviewQueue =
                computeReviewQueue(
                    attempts = learnerRepository.getAllAttempts(),
                    groups = groups,
                    zoneOffsetMillis = zoneOffsetMillis,
                    nowMillis = nowMillis,
                )
            val recommendation =
                recommend(
                    state = state,
                    groups = groups,
                    reviewDueGroupIds = reviewQueue,
                    todaySolved = todaySolved,
                ) ?: return AppResult.Failure(AppError.NoProblemAvailable)

            if (recommendation.targetDifficulty != state.currentDifficulty) {
                learnerRepository.setCurrentDifficulty(recommendation.targetDifficulty)
            }
            return AppResult.Success(recommendation)
        }
    }
