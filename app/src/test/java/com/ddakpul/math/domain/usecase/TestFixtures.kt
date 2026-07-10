package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.model.Answer
import com.ddakpul.math.domain.model.Attempt
import com.ddakpul.math.domain.model.LearnerState
import com.ddakpul.math.domain.model.MathArea
import com.ddakpul.math.domain.model.Mistake
import com.ddakpul.math.domain.model.Problem
import com.ddakpul.math.domain.model.ProblemGroup

/** 테스트용 문제/그룹/시도 빌더. */
object TestFixtures {
    fun problem(
        id: String,
        difficulty: Int,
        groupId: String = "g-$difficulty",
        area: MathArea = MathArea.NUMBER_OPERATION,
        answerIndex: Int = 0,
        choices: List<String> = listOf("가", "나", "다", "라"),
        explanation: String? = null,
        mistakes: List<Mistake> = emptyList(),
    ): Problem =
        Problem(
            id = id,
            grade = 4,
            semester = 2,
            area = area,
            conceptTags = listOf("test"),
            difficulty = difficulty,
            groupId = groupId,
            statement = "문제 $id",
            choices = choices,
            answer = Answer(answerIndex),
            explanation = explanation,
            commonMistakes = mistakes,
        )

    fun group(
        difficulty: Int,
        problems: List<Problem>,
        id: String = "g-$difficulty",
        area: MathArea = MathArea.NUMBER_OPERATION,
    ): ProblemGroup =
        ProblemGroup(
            id = id,
            area = area,
            difficulty = difficulty,
            conceptTags = listOf("test"),
            problems = problems,
        )

    fun attempt(
        problemId: String,
        isCorrect: Boolean,
        timestamp: Long = 0L,
    ): Attempt = Attempt(problemId = problemId, isCorrect = isCorrect, timeSpentSec = 10, timestamp = timestamp)

    /** 난이도 1~5 각각에 문제 3개를 담은 표준 그룹 목록. 문제 id는 "d{난이도}-{n}". */
    fun standardGroups(): List<ProblemGroup> =
        (1..5).map { difficulty ->
            group(
                difficulty = difficulty,
                problems = (1..3).map { n -> problem(id = "d$difficulty-$n", difficulty = difficulty) },
            )
        }

    fun state(
        currentDifficulty: Int,
        recentAttempts: List<Attempt> = emptyList(),
    ): LearnerState =
        LearnerState(
            currentDifficulty = currentDifficulty,
            areaMastery = emptyMap(),
            recentAttempts = recentAttempts,
        )
}
