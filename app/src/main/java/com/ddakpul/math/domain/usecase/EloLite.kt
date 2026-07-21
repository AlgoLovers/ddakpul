package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.model.Difficulty

/**
 * Elo-lite 레이팅 산술 — 적응 추천 엔진 v1의 수학 코어. **전부 정수 연산**(부동소수 금지)으로
 * 온디바이스에서 완결된다(런타임 AI 호출 0원 원칙).
 *
 * 갱신 공식: `R' = R + K × (결과 − 기대정답률)` (결과·기대는 퍼밀 단위, K는 시도 수에 따라 감쇠).
 * 기대정답률은 체스 Elo와 같은 스케일-400 로지스틱을 정수 룩업테이블로 근사한다.
 *
 * 근거:
 * - Pelánek 2016, *Applications of the Elo rating system in adaptive educational systems*
 *   (Computers & Education) — 교육용 적응 시스템에서 Elo의 유효성.
 * - Klinkenberg et al. 2011 (Math Garden) — 수학 연습 앱에서의 Elo 실전 적용.
 * - Elo 1978 / FIDE 핸드북의 레이팅차→기대승률 변환표 — 정수 룩업테이블 방식의 원형.
 * - Wilson et al. 2019, *The Eighty Five Percent Rule for optimal learning* (Nature Comms 10:4646)
 *   — 목표 기대정답률 85%.
 * - 설계 확정: docs/CONTENT_ENGINE_STRATEGY.md §2.1, docs/PEDAGOGY.md §6.
 */
internal object EloLite {
    /** 퍼밀(‰) 분모. 확률을 0~1000 정수로 다룬다 — 부동소수 금지 원칙의 구현 수단. */
    const val PERMILLE = 1_000

    /** 정답의 결과값(퍼밀). Elo의 승리 1.0에 해당. */
    const val SCORE_CORRECT_PERMILLE = 1_000

    /** 오답의 결과값(퍼밀). Elo의 패배 0.0에 해당. */
    const val SCORE_WRONG_PERMILLE = 0

    /** 난이도 [Difficulty.MIN] 문항의 레이팅 b. 척도의 원점은 임의(affine)라 1000으로 고정한다. */
    const val PROBLEM_RATING_BASE = 1_000

    /**
     * 난이도 한 칸당 레이팅 간격. 200점 = 스케일-400 로지스틱에서 기대정답률 약 76%↔50%의 차 —
     * "한 난이도 위 문제는 확연히 어렵지만 불가능하지는 않다"는 감각에 맞춘 값.
     */
    const val RATING_PER_DIFFICULTY = 200

    /**
     * 85% 규칙의 목표 기대정답률(퍼밀). Wilson et al. 2019: 오답률 ~15.87%(정답률 ~85%)에서
     * 학습 속도가 최대가 된다. 문항 선택의 조준점이다.
     */
    const val TARGET_SUCCESS_PERMILLE = 850

    /**
     * 기대정답률이 목표에서 이만큼(±) 벗어나도 선택 밴드에 허용한다(퍼밀).
     * Wilson et al. 2019의 최적점은 뾰족한 봉우리가 아니라 완만한 고원이므로,
     * ±7.5%p(775~925‰)까지는 학습 효율 손실이 작다고 보고 밴드로 묶는다.
     */
    const val TARGET_BAND_TOLERANCE_PERMILLE = 75

    /**
     * 기대정답률이 [TARGET_SUCCESS_PERMILLE](≈850‰)이 되는 학습자−문항 레이팅차.
     * 스케일-400 로지스틱에서 log10(0.85/0.15) × 400 ≈ 301 → 300으로 상수화
     * (룩업테이블의 300 구간 값이 849‰). 전략 문서의 "b ≈ θ − 약 300"이 이 값이다.
     */
    const val TARGET_RATING_GAP = 300

    /** 영역별 시도가 이 횟수 미만이면 배치(placement) 단계 — 최대 K로 빠르게 자리를 잡는다. */
    const val PLACEMENT_ATTEMPTS = 10

    /** 영역별 시도가 이 횟수 미만이면 안정화 단계 — 중간 K. */
    const val DEVELOPING_ATTEMPTS = 30

    /**
     * K 스케줄: 시도가 쌓일수록 한 번의 결과가 레이팅을 덜 흔든다 — Glicko의 RD(불확실성)
     * 감소를 정수 3단계로 근사한 것(Glickman 1999). FIDE의 신인 K=40 → 기성 K=10 감쇠와 같은 구조.
     */
    const val K_FACTOR_PLACEMENT = 64

    /** [PLACEMENT_ATTEMPTS] 이상 ~ [DEVELOPING_ATTEMPTS] 미만 구간의 K. */
    const val K_FACTOR_DEVELOPING = 32

    /** [DEVELOPING_ATTEMPTS] 이상 구간의 K — 레이팅이 자리 잡은 뒤의 완만한 갱신. */
    const val K_FACTOR_STABLE = 16

    /** 룩업테이블 상한(퍼밀). 극단 우세에서도 995‰에서 캡 — Elo 변환표들이 쓰는 관례적 천장. */
    const val MAX_EXPECTED_PERMILLE = 995

    /**
     * 레이팅차(d ≥ 0) → 기대정답률(퍼밀) 룩업테이블. 각 구간의 값은 스케일-400 로지스틱
     * `E = 1 / (1 + 10^(−d/400))`를 구간 대표점(0, 50, 100, …)에서 계산해 퍼밀로 반올림한 것.
     * 음수 차는 [expectedScorePermille]에서 `1000 − E(−d)`로 뒤집으므로 대칭이 구조적으로 보장된다.
     */
    private val EXPECTED_SCORE_BUCKETS =
        listOf(
            // upToExclusive to permille — 구간 [이전 경계, upToExclusive)의 기대정답률.
            RatingBucket(upToExclusive = 25, permille = 500), // E(0)
            RatingBucket(upToExclusive = 75, permille = 571), // E(50)
            RatingBucket(upToExclusive = 125, permille = 640), // E(100)
            RatingBucket(upToExclusive = 175, permille = 703), // E(150)
            RatingBucket(upToExclusive = 225, permille = 760), // E(200)
            RatingBucket(upToExclusive = 275, permille = 808), // E(250)
            RatingBucket(upToExclusive = 325, permille = 849), // E(300) — TARGET_RATING_GAP이 여기 떨어진다
            RatingBucket(upToExclusive = 375, permille = 882), // E(350)
            RatingBucket(upToExclusive = 425, permille = 909), // E(400)
            RatingBucket(upToExclusive = 475, permille = 930), // E(450)
            RatingBucket(upToExclusive = 550, permille = 947), // E(500)
            RatingBucket(upToExclusive = 700, permille = 969), // E(600)
            RatingBucket(upToExclusive = 900, permille = 990), // E(800)
        )

    /** 학습자에게 새 영역이 열릴 때의 초기 θ — 기대정답률 85% 조준점이 정확히 [Difficulty.DEFAULT]가 되는 값. */
    val INITIAL_ABILITY_RATING: Int = problemRating(Difficulty.DEFAULT) + TARGET_RATING_GAP

    /**
     * 문항 난이도(1~[Difficulty.MAX]) → 문항 레이팅 b. 선형 매핑 `b = BASE + (난이도−MIN) × 간격`.
     *
     * v1은 난이도에서 파생한 **정적** b만 쓴다. 문항별 응답 데이터로 b를 미세조정하는
     * 동적 갱신(양방향 Elo)은 v2로 미룬다 — docs/CONTENT_ENGINE_STRATEGY.md §2.1 적용안 1.
     */
    fun problemRating(difficulty: Int): Int = PROBLEM_RATING_BASE + (Difficulty.clamp(difficulty) - Difficulty.MIN) * RATING_PER_DIFFICULTY

    /**
     * 레이팅차(학습자 θ − 문항 b) → 기대정답률(퍼밀). 음수 차는 `1000 − E(−d)`로 계산하므로
     * `E(+d) + E(−d) = 1000`(대칭)이 항상 성립하고, [MAX_EXPECTED_PERMILLE]로 캡된다.
     */
    fun expectedScorePermille(ratingDiff: Int): Int =
        if (ratingDiff >= 0) {
            positiveExpectedPermille(ratingDiff)
        } else {
            PERMILLE - positiveExpectedPermille(-ratingDiff)
        }

    /** K 스케줄 — 해당 영역의 누적 시도 수가 많을수록 작은 K(불확실성 감소의 정수 근사). */
    fun kFactor(attemptsSoFar: Int): Int =
        when {
            attemptsSoFar < PLACEMENT_ATTEMPTS -> K_FACTOR_PLACEMENT
            attemptsSoFar < DEVELOPING_ATTEMPTS -> K_FACTOR_DEVELOPING
            else -> K_FACTOR_STABLE
        }

    /**
     * Elo 갱신 한 스텝: `R' = R + K × (결과 − 기대) / 1000` (정수 나눗셈, 0 방향 절사라
     * 정답·오답의 이동 폭이 대칭이다). 극단적 불일치(아주 쉬운 문제 정답, 아주 어려운 문제
     * 오답)에서는 `|결과 − 기대|`가 캡에 눌려 갱신이 0이 된다 — 정보가 없는 결과로 레이팅을
     * 흔들지 않는 Elo 본연의 성질이며, 쉬운 문제 반복으로 θ를 올리는 편법도 함께 막는다.
     *
     * @param attemptsSoFar 이 시도 **이전까지** 해당 영역에 누적된 시도 수(K 감쇠 입력).
     */
    fun updatedRating(
        rating: Int,
        attemptsSoFar: Int,
        problemRating: Int,
        isCorrect: Boolean,
    ): Int {
        val expected = expectedScorePermille(rating - problemRating)
        val score = if (isCorrect) SCORE_CORRECT_PERMILLE else SCORE_WRONG_PERMILLE
        return rating + kFactor(attemptsSoFar) * (score - expected) / PERMILLE
    }

    private fun positiveExpectedPermille(nonNegativeDiff: Int): Int =
        EXPECTED_SCORE_BUCKETS.firstOrNull { nonNegativeDiff < it.upToExclusive }?.permille
            ?: MAX_EXPECTED_PERMILLE

    private data class RatingBucket(
        val upToExclusive: Int,
        val permille: Int,
    )
}
