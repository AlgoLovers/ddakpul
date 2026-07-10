package com.ddakpul.math.data

import com.ddakpul.math.domain.model.Attempt
import com.ddakpul.math.domain.model.Difficulty
import com.ddakpul.math.domain.model.LearnerState
import com.ddakpul.math.domain.model.MathArea
import com.ddakpul.math.domain.model.Problem
import com.ddakpul.math.domain.model.ProblemGroup
import com.ddakpul.math.domain.model.SessionGoals
import com.ddakpul.math.domain.repository.LearnerRepository
import com.ddakpul.math.domain.repository.ProblemRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow

class FakeProblemRepository(
    private val groups: List<ProblemGroup>,
) : ProblemRepository {
    override suspend fun getAllGroups(): List<ProblemGroup> = groups

    override suspend fun getProblem(id: String): Problem? = groups.flatMap { it.problems }.firstOrNull { it.id == id }

    override suspend fun areaByProblemId(): Map<String, MathArea> = groups.flatMap { it.problems }.associate { it.id to it.area }
}

class FakeLearnerRepository(
    initialDifficulty: Int = Difficulty.DEFAULT,
) : LearnerRepository {
    private val attempts = MutableStateFlow<List<Attempt>>(emptyList())
    private val dailyGoal = MutableStateFlow(SessionGoals.DAILY_GOAL_PROBLEMS)

    var currentDifficulty: Int = initialDifficulty
        private set
    var setDifficultyCallCount: Int = 0
        private set

    val recordedAttempts: List<Attempt> get() = attempts.value

    override suspend fun getLearnerState(): LearnerState =
        LearnerState(
            currentDifficulty = currentDifficulty,
            areaMastery = emptyMap(),
            recentAttempts = attempts.value.takeLast(RECENT_WINDOW),
        )

    override suspend fun getCurrentDifficulty(): Int = currentDifficulty

    override suspend fun recordAttempt(attempt: Attempt) {
        attempts.value = attempts.value + attempt
    }

    override suspend fun setCurrentDifficulty(difficulty: Int) {
        currentDifficulty = difficulty
        setDifficultyCallCount++
    }

    override fun observeAttempts(): Flow<List<Attempt>> = attempts.asStateFlow()

    override suspend fun getAllAttempts(): List<Attempt> = attempts.value

    override fun observeDailyGoal(): Flow<Int> = dailyGoal.asStateFlow()

    override suspend fun setDailyGoal(goal: Int) {
        dailyGoal.value = goal
    }

    override suspend fun resetProgress() {
        attempts.value = emptyList()
        currentDifficulty = Difficulty.DEFAULT
    }

    private companion object {
        const val RECENT_WINDOW = 10
    }
}
