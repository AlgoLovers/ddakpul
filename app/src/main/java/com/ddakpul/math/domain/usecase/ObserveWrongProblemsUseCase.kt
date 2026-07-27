package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.model.Attempt
import com.ddakpul.math.domain.model.Problem
import com.ddakpul.math.domain.model.WrongProblem
import com.ddakpul.math.domain.model.problemsById
import com.ddakpul.math.domain.repository.LearnerRepository
import com.ddakpul.math.domain.repository.ProblemRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.emitAll
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject

/**
 * 오답 노트 스트림 — 각 문제의 '가장 최근 시도'가 오답인 문제를 마지막으로 틀린 순으로 돌려준다.
 * 리포트의 최근 오답 카드(개수 제한)와 달리 제한 없이 전체를 담아, 오답 노트 화면의 원전이 된다.
 * 시도가 바뀌면(복습 재풀이로 정답 처리되면) 자동으로 목록에서 빠진다.
 */
class ObserveWrongProblemsUseCase
    @Inject
    constructor(
        private val learnerRepository: LearnerRepository,
        private val problemRepository: ProblemRepository,
    ) {
        operator fun invoke(): Flow<List<WrongProblem>> =
            flow {
                val problemsById = problemRepository.getAllGroups().problemsById()
                emitAll(
                    learnerRepository.observeAttempts().map { attempts ->
                        selectWrongProblems(attempts, problemsById)
                    },
                )
            }
    }

/**
 * 순수 선택 로직 — 단위 테스트로 검증한다. [attempts]는 시간 오름차순이라고 가정한다.
 * 은행에서 사라진 문제(제거된 콘텐츠)는 제외하고, 마지막 시도가 오답인 문제만 최신순으로 담는다.
 */
internal fun selectWrongProblems(
    attempts: List<Attempt>,
    problemsById: Map<String, Problem>,
): List<WrongProblem> =
    attempts
        .filter { it.problemId in problemsById }
        .groupBy { it.problemId }
        .mapNotNull { (id, tries) ->
            val last = tries.last()
            if (last.isCorrect) return@mapNotNull null
            val problem = problemsById[id] ?: return@mapNotNull null
            WrongProblem(
                problem = problem,
                lastWrongAt = last.timestamp,
                wrongCount = tries.count { !it.isCorrect },
            )
        }.sortedByDescending { it.lastWrongAt }
