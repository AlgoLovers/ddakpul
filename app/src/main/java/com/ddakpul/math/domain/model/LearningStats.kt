package com.ddakpul.math.domain.model

/** 영역별 풀이 통계. */
data class AreaStat(
    val area: MathArea,
    val solved: Int,
    val correct: Int,
) {
    val accuracy: Float get() = if (solved == 0) 0f else correct.toFloat() / solved
}

/**
 * 하루 단위 학습량. [epochDay]는 로컬 자정 기준 경과 일수 — 타임존 오프셋을 더한 뒤
 * 하루(ms)로 나눈 값이라, 같은 날 밤 11시와 아침 7시가 같은 칸에 집계된다.
 */
data class DailyStat(
    val epochDay: Long,
    val solved: Int,
    val correct: Int,
    val timeSpentSec: Int,
) {
    val accuracy: Float get() = if (solved == 0) 0f else correct.toFloat() / solved
}

/** 개념 태그별 숙달 통계. 취약 개념(정답률 낮은 순)을 리포트에서 짚어주는 데 쓴다. */
data class ConceptStat(
    val concept: String,
    val area: MathArea,
    val solved: Int,
    val correct: Int,
) {
    val accuracy: Float get() = if (solved == 0) 0f else correct.toFloat() / solved
}

/** 시도 시점에 푼 문제의 난이도 — 난이도 진행(성장 곡선) 그래프의 한 점. */
data class DifficultyPoint(
    val timestamp: Long,
    val difficulty: Int,
)

/**
 * 학습 기록 전체에서 파생되는 통계 묶음. 홈(오늘 진행·스트릭)과
 * 부모용 리포트(추이·숙달도·인사이트)가 모두 이 모델 하나를 읽는다.
 */
data class LearningStats(
    val totalSolved: Int,
    val correctCount: Int,
    val currentDifficulty: Int,
    val areaStats: List<AreaStat>,
    /** epochDay 오름차순. 학습한 날만 들어 있다(빈 날은 UI에서 채움). */
    val dailyStats: List<DailyStat>,
    val conceptStats: List<ConceptStat>,
    /** 시도 순서대로의 난이도 — 성장 곡선. */
    val difficultyProgress: List<DifficultyPoint>,
    /** 오늘까지 이어진 연속 학습일. 오늘 안 했어도 어제까지 이어졌으면 살아 있다. */
    val streakDays: Int,
    val bestStreakDays: Int,
    val todaySolved: Int,
    val todayCorrect: Int,
    /** 난이도별 평균 풀이 시간(초). 시도가 없는 난이도는 키가 없다. */
    val avgTimeSecByDifficulty: Map<Int, Int>,
    /** 최근 7일 정답률. 해당 기간 시도가 없으면 null. */
    val recentAccuracy: Float?,
    /** 그 이전 7일(8~14일 전) 정답률. 해당 기간 시도가 없으면 null. */
    val previousAccuracy: Float?,
    /**
     * 오답 해소율 — 한 번이라도 틀렸던 문제 중, 그 후 다시 풀어 맞힌 문제의 비율.
     * 복습 루프가 작동한다는 증거이자 "틀림 = 나쁨이 아님" 메시지. 틀린 문제가 없으면 null.
     */
    val errorRecoveryRate: Float?,
) {
    val accuracy: Float get() = if (totalSolved == 0) 0f else correctCount.toFloat() / totalSolved
    val isEmpty: Boolean get() = totalSolved == 0
}

/** 세션(오늘의 학습) 목표 — 동기부여 UI의 기준값. */
object SessionGoals {
    /** 하루 권장 문항 수. 초4 집중 시간을 고려한 기본값(리서치 근거로 튜닝). */
    const val DAILY_GOAL_PROBLEMS = 10
}
