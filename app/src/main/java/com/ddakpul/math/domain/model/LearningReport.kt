package com.ddakpul.math.domain.model

/** 최근 N일 창의 하루 칸. 학습이 없던 날은 solved=0, accuracy=null. */
data class DayCell(
    val epochDay: Long,
    val solved: Int,
    val accuracy: Float?,
    val isToday: Boolean,
)

/**
 * 숙달 지도의 한 칸(영역×난이도). 집계 원본인 [MatrixCell]은 시도가 있는 칸만 담으므로,
 * 시도 없는 칸도 solved=0으로 채워 그리드를 항상 완성한 결과가 이것이다.
 */
data class MasteryCell(
    val area: MathArea,
    val difficulty: Int,
    val solved: Int,
    val accuracy: Float?,
)

/**
 * 학부모에게 보여줄 문장형 인사이트 — 데이터 해석을 끝낸 "말"이 차트보다 잘 읽힌다.
 * 어떤 인사이트를 띄울지는 교육 정책이라 domain에서 정하고, 문구 매핑만 화면(리소스)에서 한다.
 */
sealed interface ReportInsight {
    data class Streak(
        val days: Int,
    ) : ReportInsight

    data class AccuracyUp(
        val deltaPercentPoint: Int,
    ) : ReportInsight

    data class AccuracyDown(
        val deltaPercentPoint: Int,
    ) : ReportInsight

    data class ErrorRecovery(
        val percent: Int,
    ) : ReportInsight

    data class WeakConcept(
        val concept: String,
        val percent: Int,
    ) : ReportInsight

    data object GoalDone : ReportInsight
}

/** 이번 주(최근 7일) 요약 — 학부모 소통의 최선 관행인 "주간 요약 문단"의 재료. */
data class WeeklySummary(
    val solved: Int,
    val studyDays: Int,
    val accuracyPercent: Int,
    /** 지난주 대비 정답률 변화(%p). 비교 불가면 null. */
    val deltaPercentPoint: Int?,
    /** 보강 권장 개념. 없으면 null. */
    val weakConcept: String?,
)

/** 통계를 학부모가 읽을 수 있는 형태로 해석해 둔 한 벌. 화면은 이것을 그리기만 한다. */
data class LearningReport(
    val dayCells: List<DayCell> = emptyList(),
    val insights: List<ReportInsight> = emptyList(),
    val weeklySummary: WeeklySummary? = null,
    val masteryGrid: List<MasteryCell> = emptyList(),
) {
    companion object {
        /** 아직 통계가 흐르기 전의 빈 리포트. */
        val EMPTY = LearningReport()
    }
}
