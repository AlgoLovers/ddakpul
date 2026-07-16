package com.ddakpul.math.domain.usecase

import com.ddakpul.math.data.FakeProblemFeedbackRepository
import com.ddakpul.math.data.FakeProblemRepository
import com.ddakpul.math.domain.usecase.TestFixtures.standardGroups
import com.google.common.truth.Truth.assertThat
import kotlinx.coroutines.test.runTest
import org.junit.Test

class BuildExclusionReportUseCaseTest {
    private val feedback = FakeProblemFeedbackRepository()
    private val useCase =
        BuildExclusionReportUseCase(
            feedbackRepository = feedback,
            problemRepository = FakeProblemRepository(standardGroups()),
        )

    @Test
    fun noExclusions_returnsNull() =
        runTest {
            assertThat(useCase()).isNull()
        }

    @Test
    fun report_containsCountIdDifficultyStatementReason() =
        runTest {
            feedback.exclude("d3-1", reason = "너무 쉬움", timestampMillis = 0L)
            feedback.exclude("d4-2", reason = null, timestampMillis = 1L)

            val report = useCase()

            assertThat(report).isNotNull()
            assertThat(report!!.count).isEqualTo(2)
            assertThat(report.entries).hasSize(2)

            val first = report.entries[0]
            assertThat(first.order).isEqualTo(1)
            assertThat(first.problemId).isEqualTo("d3-1")
            assertThat(first.difficulty).isEqualTo(3)
            assertThat(first.statementPreview).contains("문제 d3-1") // 지문
            assertThat(first.reason).isEqualTo("너무 쉬움")

            assertThat(report.entries[1].problemId).isEqualTo("d4-2")
            assertThat(report.entries[1].reason).isNull()
        }

    @Test
    fun problemMissingFromBank_stillListedWithNullArea() =
        runTest {
            // 앱 업데이트로 문제은행에서 이미 사라진 문제도 목록에는 남긴다.
            feedback.exclude("ghost-1", reason = null, timestampMillis = 0L)

            val report = useCase()

            assertThat(report).isNotNull()
            val entry = report!!.entries.single()
            assertThat(entry.problemId).isEqualTo("ghost-1")
            assertThat(entry.area).isNull()
            assertThat(entry.difficulty).isNull()
            assertThat(entry.statementPreview).isEmpty()
        }
}
