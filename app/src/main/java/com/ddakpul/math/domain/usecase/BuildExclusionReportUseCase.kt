package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.model.ExclusionReport
import com.ddakpul.math.domain.repository.ProblemFeedbackRepository
import com.ddakpul.math.domain.repository.ProblemRepository
import javax.inject.Inject

/** 지문이 이보다 길면 잘라서 담는다 — 공유 텍스트가 지나치게 길어지지 않게. */
private const val STATEMENT_PREVIEW_LENGTH = 80

/**
 * 제외한 문제 목록을 구조화한 [ExclusionReport]로 만든다. 부모가 이걸 사람이 읽을
 * 텍스트(언어별)로 바꿔 개발 채널(텔레그램)로 보내면 다음 업데이트의 개선 입력이 된다.
 * 제외한 문제가 없으면 null. 텍스트 형식·언어는 presentation이 정한다(domain은 리소스를 모른다).
 */
class BuildExclusionReportUseCase
    @Inject
    constructor(
        private val feedbackRepository: ProblemFeedbackRepository,
        private val problemRepository: ProblemRepository,
    ) {
        suspend operator fun invoke(): ExclusionReport? {
            val exclusions = feedbackRepository.getAllExclusions()
            if (exclusions.isEmpty()) return null

            val entries =
                exclusions.mapIndexed { index, exclusion ->
                    val problem = problemRepository.getProblem(exclusion.problemId)
                    ExclusionReport.Entry(
                        order = index + 1,
                        problemId = exclusion.problemId,
                        area = problem?.area,
                        difficulty = problem?.difficulty,
                        statementPreview = problem?.statement?.preview().orEmpty(),
                        reason = exclusion.reason,
                    )
                }
            return ExclusionReport(count = exclusions.size, entries = entries)
        }

        private fun String.preview(): String = if (length <= STATEMENT_PREVIEW_LENGTH) this else take(STATEMENT_PREVIEW_LENGTH) + "…"
    }
