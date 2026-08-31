package com.ddakpul.math.data.repository

import com.ddakpul.math.data.local.dao.LearnerProgressDao
import com.ddakpul.math.domain.model.Difficulty
import com.ddakpul.math.domain.model.SessionGoals
import com.ddakpul.math.domain.repository.LearnerPreferencesRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

/**
 * 설정도 학습 진행과 같은 단일 행(learner_progress)에 담기지만, 저장은 필드별 UPDATE로 한다 —
 * 행 전체를 다시 쓰면 같은 순간 저장되는 현재 난이도를 덮어쓴다.
 */
@Singleton
class LearnerPreferencesRepositoryImpl
    @Inject
    constructor(
        private val progressDao: LearnerProgressDao,
    ) : LearnerPreferencesRepository {
        override fun observeDailyGoal(): Flow<Int> = progressDao.observe().map { it?.dailyGoal ?: SessionGoals.DAILY_GOAL_PROBLEMS }

        override suspend fun setDailyGoal(goal: Int) {
            ensureRow()
            progressDao.updateDailyGoal(goal)
        }

        override fun observeUnlockAllLevels(): Flow<Boolean> = progressDao.observe().map { it?.unlockAllLevels ?: false }

        override suspend fun getUnlockAllLevels(): Boolean = progressDao.get()?.unlockAllLevels ?: false

        override suspend fun setUnlockAllLevels(enabled: Boolean) {
            ensureRow()
            progressDao.updateUnlockAllLevels(enabled)
        }

        private suspend fun ensureRow() = progressDao.insertDefaultIfAbsent(Difficulty.DEFAULT, SessionGoals.DAILY_GOAL_PROBLEMS)
    }
