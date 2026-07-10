package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.model.MathArea
import com.ddakpul.math.domain.repository.ProblemFeedbackRepository
import com.ddakpul.math.domain.repository.ProblemRepository
import javax.inject.Inject

/** 지문이 이보다 길면 잘라서 담는다 — 공유 텍스트가 지나치게 길어지지 않게. */
private const val STATEMENT_PREVIEW_LENGTH = 80

/**
 * 제외한 문제 목록을 사람이 읽을 공유 텍스트로 만든다. 부모가 이 텍스트를
 * 개발 채널(텔레그램)로 보내면 다음 업데이트에서 문제은행 개선의 입력이 된다.
 * 제외한 문제가 없으면 null.
 */
class BuildExclusionReportUseCase
    @Inject
    constructor(
        private val feedbackRepository: ProblemFeedbackRepository,
        private val problemRepository: ProblemRepository,
    ) {
        suspend operator fun invoke(): String? {
            val exclusions = feedbackRepository.getAllExclusions()
            if (exclusions.isEmpty()) return null

            val lines =
                exclusions.mapIndexed { index, exclusion ->
                    val problem = problemRepository.getProblem(exclusion.problemId)
                    val header =
                        problem?.let { "[${it.id} · ${it.area.koreanLabel()} · 난이도 ${it.difficulty}]" }
                            ?: "[${exclusion.problemId} · 문제은행에서 이미 삭제됨]"
                    val statement = problem?.statement?.preview().orEmpty()
                    val reason = exclusion.reason?.let { "\n   이유: $it" }.orEmpty()
                    "${index + 1}. $header\n   $statement$reason"
                }
            return buildString {
                appendLine("📋 딱풀 문제 피드백 — 별로예요 ${exclusions.size}문제")
                appendLine()
                append(lines.joinToString("\n"))
            }
        }

        private fun String.preview(): String = if (length <= STATEMENT_PREVIEW_LENGTH) this else take(STATEMENT_PREVIEW_LENGTH) + "…"

        // 공유 텍스트용 한글 라벨. 화면 표시는 presentation의 리소스 매핑을 쓰지만,
        // domain이 만드는 내보내기 텍스트는 리소스를 참조할 수 없어 여기서 매핑한다.
        private fun MathArea.koreanLabel(): String =
            when (this) {
                MathArea.NUMBER_OPERATION -> "수와 연산"
                MathArea.CHANGE_RELATION -> "변화와 관계"
                MathArea.SHAPE_MEASUREMENT -> "도형과 측정"
                MathArea.DATA_POSSIBILITY -> "자료와 가능성"
            }
    }
