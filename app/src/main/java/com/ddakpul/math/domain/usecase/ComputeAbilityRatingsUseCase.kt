package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.model.AbilityRating
import com.ddakpul.math.domain.model.Attempt
import com.ddakpul.math.domain.model.MathArea
import com.ddakpul.math.domain.model.ProblemGroup
import com.ddakpul.math.domain.model.problemsById
import javax.inject.Inject

/**
 * 영역별 학습자 능력 레이팅 θ — Elo-lite 적응 엔진 v1의 상태 복원기.
 *
 * [ComputeReviewQueueUseCase]와 같은 **replay 패턴**: θ를 DB에 저장하지 않고 전체 풀이
 * 기록을 시간순으로 재생해 복원한다. 스키마 변경이 없어 마이그레이션 프리이고, 갱신 공식·상수를
 * 바꿔도 과거 기록만으로 즉시 재계산된다. 시도마다 [EloLite.updatedRating] 한 스텝씩 적용하며,
 * 영역이 다르면 서로 완전히 독립이다(한 영역의 시도는 다른 영역 θ에 영향 0).
 *
 * ⚠️ 아직 추천 흐름에 배선되지 않은 병행 프로토타입 — [RecommendNextProblemUseCase]는 그대로다.
 * 연결은 다음 슬라이스에서 한다(docs/CONTENT_ENGINE_STRATEGY.md §2.1 적용안 2~4).
 */
class ComputeAbilityRatingsUseCase
    @Inject
    constructor() {
        /** @param attempts 시간 오름차순(과거→최신) 전체 시도 기록. */
        operator fun invoke(
            attempts: List<Attempt>,
            groups: List<ProblemGroup>,
        ): Map<MathArea, AbilityRating> = computeAbilityRatings(attempts, groups)
    }

/**
 * 순수 로직 — 단위 테스트로 검증한다. [attempts]는 시간 오름차순.
 * 결과 맵에는 4개 영역이 항상 모두 들어 있다(기록 없는 영역 = 초기 θ, 시도 0회).
 * 문제은행에 없는 problemId의 시도는 무시한다(삭제·교체된 구 문항 방어).
 */
internal fun computeAbilityRatings(
    attempts: List<Attempt>,
    groups: List<ProblemGroup>,
): Map<MathArea, AbilityRating> {
    val problemsById = groups.problemsById()
    val ratings =
        MathArea.entries.associateWithTo(mutableMapOf()) {
            AbilityRating(rating = EloLite.INITIAL_ABILITY_RATING, attemptCount = 0)
        }
    attempts.forEach { attempt ->
        val problem = problemsById[attempt.problemId] ?: return@forEach
        val current = ratings.getValue(problem.area)
        ratings[problem.area] =
            AbilityRating(
                rating =
                    EloLite.updatedRating(
                        rating = current.rating,
                        attemptsSoFar = current.attemptCount,
                        problemRating = EloLite.problemRating(problem.difficulty),
                        isCorrect = attempt.isCorrect,
                    ),
                attemptCount = current.attemptCount + 1,
            )
    }
    return ratings
}
