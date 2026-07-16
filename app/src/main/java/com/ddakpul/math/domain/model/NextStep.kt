package com.ddakpul.math.domain.model

/**
 * 리포트의 '다음 한 걸음' — 통계를 실행 가능한 코칭 한 줄로 바꾼 결과(딱풀 핵심 축: 피드백).
 * 문구는 화면(리소스)에서 매핑하고, 여기서는 '무엇을 권하는지'와 '지금 풀기로 이어갈 수
 * 있는지'만 담는다.
 */
sealed interface NextStep {
    /** 카드에서 '지금 풀기'로 바로 학습을 이어갈 만한 권유인지. */
    val canSolveNow: Boolean

    /** 오늘 아직 한 문제도 안 풀었을 때 — 습관을 잇도록. */
    data object StartToday : NextStep {
        override val canSolveNow = true
    }

    /** 특정 영역이 뚜렷이 약할 때 — 그 영역을 집중하도록. */
    data class FocusArea(
        val area: MathArea,
    ) : NextStep {
        override val canSolveNow = true
    }

    /** 최근 정답률이 높아 더 어려운 난이도로 갈 준비가 됐을 때. */
    data object ReadyForHarder : NextStep {
        override val canSolveNow = true
    }

    /** 연속 학습이 이어지는 중 — 흐름을 지키도록. */
    data class KeepStreak(
        val days: Int,
    ) : NextStep {
        override val canSolveNow = false
    }

    /** 특별한 신호가 없을 때의 기본 격려(과정 중심). */
    data object Encourage : NextStep {
        override val canSolveNow = false
    }
}
