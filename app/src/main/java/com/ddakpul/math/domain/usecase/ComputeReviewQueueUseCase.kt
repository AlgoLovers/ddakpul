package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.model.Attempt
import com.ddakpul.math.domain.model.ProblemGroup
import javax.inject.Inject
import kotlin.math.min

/**
 * Leitner 박스 간격(일). 박스 n의 복습이 성공하면 n+1로 승급, 실패하면 1로 강등.
 * 간격 반복의 효과는 메타분석으로 확립되어 있다(Cepeda; docs/PEDAGOGY.md).
 */
internal val REVIEW_INTERVALS_DAYS = listOf(1L, 3L, 7L, 14L, 30L)

/** 숙달 판정 — 그룹에서 이만큼 연속 정답이면 복습 대상에 들어간다(승급 규칙과 동일 감각). */
internal const val MASTERY_STREAK = 2

/**
 * 오늘 복습이 만기된 그룹 ID 목록(가장 오래 밀린 것부터).
 *
 * 상태를 따로 저장하지 않고 전체 풀이 기록을 재생(replay)해서 박스를 복원한다 —
 * 오프라인 우선 원칙에 맞고, 마이그레이션 없이 도입할 수 있다.
 */
class ComputeReviewQueueUseCase
    @Inject
    constructor() {
        operator fun invoke(
            attempts: List<Attempt>,
            groups: List<ProblemGroup>,
            zoneOffsetMillis: Long,
            nowMillis: Long,
        ): List<String> = computeReviewQueue(attempts, groups, zoneOffsetMillis, nowMillis)
    }

private data class LeitnerState(
    val box: Int,
    val dueDay: Long,
)

/** 순수 로직 — 단위 테스트로 검증한다. [attempts]는 시간 오름차순. */
internal fun computeReviewQueue(
    attempts: List<Attempt>,
    groups: List<ProblemGroup>,
    zoneOffsetMillis: Long,
    nowMillis: Long,
): List<String> {
    val today = epochDay(nowMillis, zoneOffsetMillis)
    val groupIdByProblemId =
        groups
            .flatMap { group -> group.problems.map { it.id to group.id } }
            .toMap()

    return attempts
        .groupBy { groupIdByProblemId[it.problemId] }
        .mapNotNull { (groupId, groupAttempts) ->
            if (groupId == null) return@mapNotNull null
            val state = replayLeitner(groupAttempts, zoneOffsetMillis) ?: return@mapNotNull null
            if (today >= state.dueDay) groupId to (today - state.dueDay) else null
        }.sortedByDescending { (_, overdueDays) -> overdueDays }
        .map { (groupId, _) -> groupId }
}

/** @return 아직 숙달 전이면 null, 숙달했으면 현재 박스와 다음 만기일. */
private fun replayLeitner(
    groupAttempts: List<Attempt>,
    zoneOffsetMillis: Long,
): LeitnerState? {
    var box = 0
    var dueDay = Long.MAX_VALUE
    var streak = 0

    groupAttempts.forEach { attempt ->
        val day = epochDay(attempt.timestamp, zoneOffsetMillis)
        if (box == 0) {
            streak = if (attempt.isCorrect) streak + 1 else 0
            if (streak >= MASTERY_STREAK) {
                box = 1
                dueDay = day + REVIEW_INTERVALS_DAYS[box - 1]
            }
        } else {
            // 숙달 이후의 모든 접촉은 복습으로 취급 — 성공은 승급, 실패는 처음 박스로.
            box = if (attempt.isCorrect) min(box + 1, REVIEW_INTERVALS_DAYS.size) else 1
            dueDay = day + REVIEW_INTERVALS_DAYS[box - 1]
        }
    }
    return if (box == 0) null else LeitnerState(box = box, dueDay = dueDay)
}
