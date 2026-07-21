package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.model.Difficulty
import com.ddakpul.math.domain.model.TargetDifficultyBand
import javax.inject.Inject
import kotlin.math.abs

/**
 * 85% 규칙 문항 선택 밴드 — 학습자 θ(한 영역의 [com.ddakpul.math.domain.model.AbilityRating.rating])에서
 * 기대정답률이 목표 850‰(Wilson et al. 2019)에 가장 가까운 난이도(target)와, 허용 오차
 * ±[EloLite.TARGET_BAND_TOLERANCE_PERMILLE] 안에 드는 난이도 구간(band)을 계산한다.
 *
 * ZPD(Vygotsky)·바람직한 어려움(Bjork)의 정량화: θ보다 [EloLite.TARGET_RATING_GAP]만큼 아래
 * 레이팅의 문항이 조준점이 된다("b ≈ θ − 300", docs/CONTENT_ENGINE_STRATEGY.md §2.1 적용안 3).
 *
 * ⚠️ 아직 추천 흐름에 배선되지 않은 병행 프로토타입 — 연결은 다음 슬라이스에서.
 */
class SuggestTargetDifficultyUseCase
    @Inject
    constructor() {
        /** @param abilityRating 한 영역의 학습자 θ (replay로 복원한 [ComputeAbilityRatingsUseCase]의 출력). */
        operator fun invoke(abilityRating: Int): TargetDifficultyBand = suggestTargetDifficulty(abilityRating)
    }

/**
 * 순수 로직 — 단위 테스트로 검증한다.
 *
 * target = 기대정답률이 목표에서 가장 덜 벗어나는 난이도. 동률이면(θ가 문항 범위를 한참
 * 벗어나 기대값이 캡에 눌린 경우) 이상 레이팅 `θ − TARGET_RATING_GAP`에 문항 레이팅이 가장
 * 가까운 난이도로, 그래도 동률이면 더 어려운 쪽(살짝 위 도전)으로 푼다 — 이 규칙이
 * [Difficulty.MIN]/[Difficulty.MAX]로의 자연스러운 clamp를 만든다.
 * band = 허용 오차 안의 난이도들의 최소~최대(기대정답률이 난이도에 단조라 항상 연속 구간).
 * 오차 안에 드는 난이도가 하나도 없으면 band는 target 하나로 줄어든다.
 */
internal fun suggestTargetDifficulty(abilityRating: Int): TargetDifficultyBand {
    val idealProblemRating = abilityRating - EloLite.TARGET_RATING_GAP
    val candidates =
        (Difficulty.MIN..Difficulty.MAX).map { difficulty ->
            val problemRating = EloLite.problemRating(difficulty)
            val expected = EloLite.expectedScorePermille(abilityRating - problemRating)
            TargetCandidate(
                difficulty = difficulty,
                deviation = abs(expected - EloLite.TARGET_SUCCESS_PERMILLE),
                ratingDistance = abs(problemRating - idealProblemRating),
            )
        }
    // candidates는 Difficulty.MIN..MAX에서 만들어져 절대 비지 않는다.
    val target =
        candidates.minWith(
            compareBy<TargetCandidate> { it.deviation }
                .thenBy { it.ratingDistance }
                .thenByDescending { it.difficulty },
        )
    val withinBand = candidates.filter { it.deviation <= EloLite.TARGET_BAND_TOLERANCE_PERMILLE }
    return TargetDifficultyBand(
        targetDifficulty = target.difficulty,
        minDifficulty = withinBand.minOfOrNull { it.difficulty } ?: target.difficulty,
        maxDifficulty = withinBand.maxOfOrNull { it.difficulty } ?: target.difficulty,
    )
}

private data class TargetCandidate(
    val difficulty: Int,
    val deviation: Int,
    val ratingDistance: Int,
)
