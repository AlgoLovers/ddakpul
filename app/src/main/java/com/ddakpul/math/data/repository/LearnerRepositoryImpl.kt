package com.ddakpul.math.data.repository

import com.ddakpul.math.data.local.dao.AttemptDao
import com.ddakpul.math.data.local.dao.LearnerProgressDao
import com.ddakpul.math.data.local.entity.LearnerProgressEntity
import com.ddakpul.math.data.mapper.toDomain
import com.ddakpul.math.data.mapper.toEntity
import com.ddakpul.math.domain.model.Attempt
import com.ddakpul.math.domain.model.Difficulty
import com.ddakpul.math.domain.model.LearnerState
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
            progressDao.upsert(LearnerProgressEntity(currentDifficulty = Difficulty.clamp(difficulty)))
        }

        override fun observeAttempts(): Flow<List<Attempt>> = attemptDao.observeAll().map { entities -> entities.map { it.toDomain() } }

        override suspend fun resetProgress() {
            attemptDao.deleteAll()
            progressDao.deleteAll()
        }

        private companion object {
            const val RECENT_WINDOW = 10
        }
    }
