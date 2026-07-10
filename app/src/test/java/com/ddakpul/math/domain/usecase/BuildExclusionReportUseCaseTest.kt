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
    fun report_containsCountIdAndStatement() =
        runTest {
            feedback.exclude("d3-1", reason = "너무 쉬움", timestampMillis = 0L)
            feedback.exclude("d4-2", reason = null, timestampMillis = 1L)

            val report = useCase()

            assertThat(report).isNotNull()
            assertThat(report).contains("2문제")
            assertThat(report).contains("d3-1")
            assertThat(report).contains("문제 d3-1") // 지문
            assertThat(report).contains("난이도 3")
            assertThat(report).contains("이유: 너무 쉬움")
            assertThat(report).contains("d4-2")
        }

    @Test
    fun problemMissingFromBank_stillListed() =
        runTest {
            // 앱 업데이트로 문제은행에서 이미 사라진 문제도 목록에는 남긴다.
            feedback.exclude("ghost-1", reason = null, timestampMillis = 0L)

            val report = useCase()

            assertThat(report).contains("ghost-1")
            assertThat(report).contains("이미 삭제됨")
        }
}
