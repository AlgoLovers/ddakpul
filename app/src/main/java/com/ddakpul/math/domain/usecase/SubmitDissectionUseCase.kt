package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.model.Attempt
import com.ddakpul.math.domain.model.Cell
import com.ddakpul.math.domain.model.Problem
import com.ddakpul.math.domain.repository.LearnerRepository
import javax.inject.Inject

/**
 * 격자 등분 퍼즐의 답(칸→조각 배정)을 검증하고 그 시도를 기록한다. 4지선다의 [SubmitAnswerUseCase]에
 * 대응하는 구성형 경로 — 정답 인덱스 대신 [ValidateDissectionUseCase]로 채점한다.
 * 시도 기록은 동일해서(정오답·시간) 추천·통계가 등분 문제도 똑같이 다룬다.
 */
class SubmitDissectionUseCase
    @Inject
    constructor(
        private val learnerRepository: LearnerRepository,
        private val validate: ValidateDissectionUseCase,
    ) {
        suspend operator fun invoke(
            problem: Problem,
            assignment: Map<Cell, Int>,
            timeSpentSec: Int,
            timestamp: Long,
        ): DissectionValidation {
            val puzzle =
                problem.dissection
                    ?: return DissectionValidation(false, DissectionError.INCOMPLETE)
            val result = validate(puzzle, assignment)
            learnerRepository.recordAttempt(
                Attempt(
                    problemId = problem.id,
                    isCorrect = result.isValid,
                    timeSpentSec = timeSpentSec,
                    timestamp = timestamp,
                ),
            )
            return result
        }
    }
