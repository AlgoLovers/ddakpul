package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.model.MathArea
import com.ddakpul.math.domain.usecase.TestFixtures.attempt
import com.google.common.truth.Truth.assertThat
import org.junit.Test

class BuildReportTest {
    private val areaIndex =
        mapOf(
            "num1" to MathArea.NUMBER_OPERATION,
            "num2" to MathArea.NUMBER_OPERATION,
            "geo1" to MathArea.SHAPE_MEASUREMENT,
        )

    @Test
    fun aggregatesTotalsAndAccuracy() {
        val attempts =
            listOf(
                attempt("num1", true),
                attempt("num2", false),
                attempt("geo1", true),
            )

        val report = buildReport(attempts, areaIndex, currentDifficulty = 3)

        assertThat(report.totalSolved).isEqualTo(3)
        assertThat(report.correctCount).isEqualTo(2)
        assertThat(report.accuracy).isWithin(TOLERANCE).of(2f / 3f)
        assertThat(report.currentDifficulty).isEqualTo(3)
    }

    @Test
    fun aggregatesPerAreaStats() {
        val attempts =
            listOf(
                attempt("num1", true),
                attempt("num2", false),
                attempt("geo1", true),
            )

        val report = buildReport(attempts, areaIndex, currentDifficulty = 2)

        val numberStat = report.areaStats.first { it.area == MathArea.NUMBER_OPERATION }
        assertThat(numberStat.solved).isEqualTo(2)
        assertThat(numberStat.correct).isEqualTo(1)

        val shapeStat = report.areaStats.first { it.area == MathArea.SHAPE_MEASUREMENT }
        assertThat(shapeStat.solved).isEqualTo(1)
        assertThat(shapeStat.correct).isEqualTo(1)

        // 시도가 없는 영역은 0/0.
        val dataStat = report.areaStats.first { it.area == MathArea.DATA_POSSIBILITY }
        assertThat(dataStat.solved).isEqualTo(0)
        assertThat(dataStat.accuracy).isEqualTo(0f)
    }

    @Test
    fun emptyAttempts_isEmptyReport() {
        val report = buildReport(emptyList(), areaIndex, currentDifficulty = 2)

        assertThat(report.isEmpty).isTrue()
        assertThat(report.accuracy).isEqualTo(0f)
    }

    private companion object {
        const val TOLERANCE = 0.0001f
    }
}
