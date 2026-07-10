package com.ddakpul.math.domain.usecase

import com.ddakpul.math.core.common.AppError
import com.ddakpul.math.core.common.AppResult
import com.ddakpul.math.domain.model.Recommendation
import com.ddakpul.math.domain.repository.LearnerRepository
import com.ddakpul.math.domain.repository.ProblemRepository
import javax.inject.Inject

/**
 * 저장소에서 문제은행과 학습자 상태를 읽어 [RecommendNextProblemUseCase]로 다음 문제를 정하고,
 * 난이도가 바뀌었으면 진행 상태에 반영한다. ViewModel은 이 UseCase만 호출한다.
 */
class GetNextProblemUseCase
    @Inject
    constructor(
        private val problemRepository: ProblemRepository,
        private val learnerRepository: LearnerRepository,
        private val recommend: RecommendNextProblemUseCase,
    ) {
        suspend operator fun invoke(): AppResult<Recommendation> {
            val groups = problemRepository.getAllGroups()
            if (groups.isEmpty()) return AppResult.Failure(AppError.EmptyProblemBank)

            val state = learnerRepository.getLearnerState()
            val recommendation =
                recommend(state, groups)
                    ?: return AppResult.Failure(AppError.NoProblemAvailable)

            if (recommendation.targetDifficulty != state.currentDifficulty) {
                learnerRepository.setCurrentDifficulty(recommendation.targetDifficulty)
            }
            return AppResult.Success(recommendation)
        }
    }
