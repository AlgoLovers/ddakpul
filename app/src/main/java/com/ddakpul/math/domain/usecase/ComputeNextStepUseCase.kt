package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.model.LearningStats
import com.ddakpul.math.domain.model.NextStep
import javax.inject.Inject

/**
 * 학습 통계를 '다음 한 걸음'(실행 가능한 코칭 한 줄)으로 요약한다 — 딱풀 핵심 축 '피드백'.
 * 통계를 '보여주기'에서 멈추지 않고 '다음에 뭘 하면 좋은지'로 이어 준다.
 *
 * 우선순위: 오늘 시작 > 취약 영역 집중 > 상향 도전 준비 > 연속 유지 > 기본 격려.
 * 순수 함수(도메인) + 단위 테스트로 각 규칙을 검증한다.
 */
class ComputeNextStepUseCase
    @Inject
    constructor() {
        operator fun invoke(stats: LearningStats): NextStep {
            // 1) 오늘 아직 안 풀었으면 이어가기부터(습관이 최우선).
            if (stats.todaySolved == 0) return NextStep.StartToday

            // 2) 뚜렷이 약한 영역이 있으면 그곳을 집중.
            val weakArea =
                stats.areaStats
                    .filter { it.solved >= MIN_SOLVED_FOR_AREA }
                    .minByOrNull { it.accuracy }
                    ?.takeIf { it.accuracy < WEAK_ACCURACY }
            if (weakArea != null) return NextStep.FocusArea(weakArea.area)

            // 3) 최근 정답률이 높으면 상향 도전 준비.
            val recent = stats.recentAccuracy
            if (recent != null && recent >= READY_ACCURACY) return NextStep.ReadyForHarder

            // 4) 연속 학습이 이어지면 흐름 유지 격려.
            if (stats.streakDays >= MIN_STREAK) return NextStep.KeepStreak(stats.streakDays)

            // 5) 기본 격려(과정 중심).
            return NextStep.Encourage
        }

        private companion object {
            /** 영역 취약 판정을 위한 최소 시도 수(표본 부족한데 단정하지 않도록). */
            const val MIN_SOLVED_FOR_AREA = 3

            /** 이 정답률 미만이면 '취약 영역'. */
            const val WEAK_ACCURACY = 0.6f

            /** 최근 7일 정답률이 이 이상이면 상향 도전 준비. */
            const val READY_ACCURACY = 0.85f

            /** 연속 유지 격려를 띄우는 최소 연속일. */
            const val MIN_STREAK = 2
        }
    }
