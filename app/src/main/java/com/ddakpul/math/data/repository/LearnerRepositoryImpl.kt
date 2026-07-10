package com.ddakpul.math.data.repository

import com.ddakpul.math.data.local.dao.AttemptDao
import com.ddakpul.math.data.local.dao.LearnerProgressDao
import com.ddakpul.math.data.local.entity.LearnerProgressEntity
import com.ddakpul.math.data.mapper.toDomain
import com.ddakpul.math.data.mapper.toEntity
import com.ddakpul.math.domain.model.Attempt
import com.ddakpul.math.domain.model.Difficulty
import com.ddakpul.math.domain.model.LearnerState
import com.ddakpul.math.domain.model.SessionGoals
import com.ddakpul.math.domain.repository.LearnerRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class LearnerRepositoryImpl
    @Inject
    constructor(
        private val attemptDao: AttemptDao,
        private val progressDao: LearnerProgressDao,
    ) : LearnerRepository {
        override suspend fun getLearnerState(): LearnerState {
            // DAO는 최신순으로 주므로, 추천 규칙이 기대하는 시간 오름차순으로 뒤집는다.
            val recent = attemptDao.recent(RECENT_WINDOW).map { it.toDomain() }.reversed()
            return LearnerState(
                currentDifficulty = getCurrentDifficulty(),
                areaMastery = emptyMap(),
                recentAttempts = recent,
            )
        }

        override suspend fun getCurrentDifficulty(): Int = progressDao.get()?.currentDifficulty ?: Difficulty.DEFAULT

        override suspend fun recordAttempt(attempt: Attempt) {
            attemptDao.insert(attempt.toEntity())
        }

        override suspend fun setCurrentDifficulty(difficulty: Int) {
            val clamped = Difficulty.clamp(difficulty)
            // 행 전체를 새로 쓰면 dailyGoal이 기본값으로 덮이므로 읽어서 수정한다.
            val current = progressDao.get()
            progressDao.upsert(
                current?.copy(currentDifficulty = clamped)
                    ?: LearnerProgressEntity(currentDifficulty = clamped),
            )
        }

        override fun observeAttempts(): Flow<List<Attempt>> = attemptDao.observeAll().map { entities -> entities.map { it.toDomain() } }

        override suspend fun getAllAttempts(): List<Attempt> = attemptDao.getAll().map { it.toDomain() }

        override fun observeDailyGoal(): Flow<Int> = progressDao.observe().map { it?.dailyGoal ?: SessionGoals.DAILY_GOAL_PROBLEMS }

        override suspend fun setDailyGoal(goal: Int) {
            val current = progressDao.get()
            progressDao.upsert(
                current?.copy(dailyGoal = goal)
                    ?: LearnerProgressEntity(currentDifficulty = Difficulty.DEFAULT, dailyGoal = goal),
            )
        }

        override suspend fun resetProgress() {
            attemptDao.deleteAll()
            // 하루 목표는 학습 기록이 아니라 아이의 선택이므로 유지하고, 난이도만 처음으로.
            val current = progressDao.get()
            if (current != null) {
                progressDao.upsert(current.copy(currentDifficulty = Difficulty.DEFAULT))
            }
        }

        private companion object {
            const val RECENT_WINDOW = 10
        }
    }
