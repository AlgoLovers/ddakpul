package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.model.Attempt
import com.ddakpul.math.domain.model.MathArea
import com.ddakpul.math.domain.model.Problem
import com.ddakpul.math.domain.model.ProblemGroup
import com.ddakpul.math.domain.repository.LearnerRepository
import com.ddakpul.math.domain.repository.ProblemRepository
import javax.inject.Inject
import kotlin.math.abs
import kotlin.random.Random

/** 학습지 출제 방식. */
enum class WorksheetSource {
    /** 딱풀 추천 — 현재 난이도 주변에서 최근에 안 푼 문제. */
    RECOMMENDED,

    /** 오답 위주 — 최근에 틀린 문제를 먼저 담고 나머지를 추천으로 채움(오답노트 인쇄). */
    WRONG_FIRST,
}

/** 학습지 구성 옵션. [area]가 null이면 전체 영역. */
data class WorksheetSpec(
    val count: Int,
    val source: WorksheetSource,
    val area: MathArea? = null,
)

/**
 * 인쇄용 학습지에 담을 문제를 고른다. 선택 자체는 순수 함수
 * [selectWorksheetProblems]가 하고, 여기서는 저장소에서 입력만 모은다.
 */
class BuildWorksheetUseCase
    @Inject
    constructor(
        private val problemRepository: ProblemRepository,
        private val learnerRepository: LearnerRepository,
    ) {
        suspend operator fun invoke(
            spec: WorksheetSpec,
            random: Random = Random.Default,
        ): List<Problem> {
            val groups = problemRepository.getAllGroups()
            val state = learnerRepository.getLearnerState()
            return selectWorksheetProblems(
                spec = spec,
                groups = groups,
                recentAttempts = state.recentAttempts,
                currentDifficulty = state.currentDifficulty,
                random = random,
            )
        }
    }

/** 학습지 선택에서 "현재 난이도 주변"으로 인정할 난이도 차. */
private const val DIFFICULTY_BAND = 1

/**
 * 순수 선택 로직 — 단위 테스트로 검증한다.
 *
 * 1. [WorksheetSource.WRONG_FIRST]면 최근 오답 문제(최신 우선, 중복 제거)를 먼저 담는다.
 * 2. 나머지는 현재 난이도 ±[DIFFICULTY_BAND] 범위에서, 최근에 풀지 않은 문제를 우선으로 랜덤 선발.
 * 3. 마지막으로 같은 그룹(유사 유형)이 연속하지 않도록 섞는다 — 블록 연습 대신
 *    인터리빙이 장기 기억에 유리하다(Rohrer 2020).
 */
internal fun selectWorksheetProblems(
    spec: WorksheetSpec,
    groups: List<ProblemGroup>,
    recentAttempts: List<Attempt>,
    currentDifficulty: Int,
    random: Random,
): List<Problem> {
    val all =
        groups
            .flatMap { it.problems }
            .filter { spec.area == null || it.area == spec.area }
    if (all.isEmpty() || spec.count <= 0) return emptyList()
    val byId = all.associateBy { it.id }

    val selected = mutableListOf<Problem>()
    if (spec.source == WorksheetSource.WRONG_FIRST) {
        val wrongIdsLatestFirst =
            recentAttempts
                .filter { !it.isCorrect }
                .map { it.problemId }
                .reversed()
                .distinct()
        wrongIdsLatestFirst
            .mapNotNull { byId[it] }
            .take(spec.count)
            .forEach { selected.add(it) }
    }

    val solvedRecently = recentAttempts.mapTo(mutableSetOf()) { it.problemId }
    val selectedIds = selected.mapTo(mutableSetOf()) { it.id }
    val remaining = all.filter { it.id !in selectedIds }
    val band = remaining.filter { abs(it.difficulty - currentDifficulty) <= DIFFICULTY_BAND }
    val pool = band.ifEmpty { remaining }
    val (fresh, seen) = pool.partition { it.id !in solvedRecently }
    selected += (fresh.shuffled(random) + seen.shuffled(random)).take(spec.count - selected.size)

    return interleaveByGroup(selected, random)
}

/** 같은 그룹이 연속하지 않도록 그리디하게 배치한다(불가능하면 그대로 잇는다). */
private fun interleaveByGroup(
    problems: List<Problem>,
    random: Random,
): List<Problem> {
    val remaining = problems.shuffled(random).toMutableList()
    val result = mutableListOf<Problem>()
    while (remaining.isNotEmpty()) {
        val lastGroup = result.lastOrNull()?.groupId
        val next =
            remaining.firstOrNull { it.groupId != lastGroup }
                ?: remaining.first()
        remaining.remove(next)
        result.add(next)
    }
    return result
}
