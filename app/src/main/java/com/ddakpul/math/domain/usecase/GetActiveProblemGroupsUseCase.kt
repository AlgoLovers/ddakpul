package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.model.ProblemGroup
import com.ddakpul.math.domain.repository.ProblemFeedbackRepository
import com.ddakpul.math.domain.repository.ProblemRepository
import javax.inject.Inject

/**
 * 문제은행에서 "별로예요"로 제외된 문제를 걸러낸 그룹 목록을 돌려준다.
 * 추천([GetNextProblemUseCase])과 학습지([BuildWorksheetUseCase]) 등 출제가 일어나는
 * 모든 경로는 원본 대신 이 UseCase를 거쳐야 제외가 빠짐없이 적용된다.
 */
class GetActiveProblemGroupsUseCase
    @Inject
    constructor(
        private val problemRepository: ProblemRepository,
        private val feedbackRepository: ProblemFeedbackRepository,
    ) {
        suspend operator fun invoke(): List<ProblemGroup> {
            val excluded = feedbackRepository.getExcludedIds()
            val groups = problemRepository.getAllGroups()
            if (excluded.isEmpty()) return groups
            return groups
                .map { group -> group.copy(problems = group.problems.filterNot { it.id in excluded }) }
                .filter { it.problems.isNotEmpty() }
        }
    }
