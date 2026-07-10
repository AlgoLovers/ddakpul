package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.model.AreaStat
import com.ddakpul.math.domain.model.Attempt
import com.ddakpul.math.domain.model.LearnerReport
import com.ddakpul.math.domain.model.MathArea
import com.ddakpul.math.domain.repository.LearnerRepository
import com.ddakpul.math.domain.repository.ProblemRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.emitAll
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject

/** 학습 기록을 부모용 리포트로 집계해 스트림으로 노출한다. */
class ObserveLearnerReportUseCase
    @Inject
    constructor(
        private val learnerRepository: LearnerRepository,
        private val problemRepository: ProblemRepository,
    ) {
        operator fun invoke(): Flow<LearnerReport> =
            flow {
                val areaIndex = problemRepository.areaByProblemId()
                emitAll(
                    learnerRepository.observeAttempts().map { attempts ->
                        buildReport(attempts, areaIndex, learnerRepository.getCurrentDifficulty())
                    },
                )
            }
    }

/** 순수 집계 로직 — 단위 테스트로 검증한다. */
internal fun buildReport(
    attempts: List<Attempt>,
    areaIndex: Map<String, MathArea>,
    currentDifficulty: Int,
): LearnerReport {
    val areaStats =
        MathArea.entries.map { area ->
            val inArea = attempts.filter { areaIndex[it.problemId] == area }
            AreaStat(area = area, solved = inArea.size, correct = inArea.count { it.isCorrect })
        }
    return LearnerReport(
        totalSolved = attempts.size,
        correctCount = attempts.count { it.isCorrect },
        currentDifficulty = currentDifficulty,
        areaStats = areaStats,
    )
}
