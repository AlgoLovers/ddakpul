package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.model.Problem
import com.ddakpul.math.domain.repository.ProblemRepository
import javax.inject.Inject

/** 문제 하나를 id로 불러온다 — 오답 노트에서 특정 문제를 다시 풀 때 쓴다. 없으면 null. */
class GetProblemByIdUseCase
    @Inject
    constructor(
        private val problemRepository: ProblemRepository,
    ) {
        suspend operator fun invoke(id: String): Problem? = problemRepository.getProblem(id)
    }
