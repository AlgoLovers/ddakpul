package com.ddakpul.math.data.repository

import com.ddakpul.math.data.local.dao.LearnerProgressDao
import com.ddakpul.math.domain.model.Difficulty
import com.ddakpul.math.domain.model.SessionGoals
import com.ddakpul.math.domain.repository.OnboardingRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

/** 온보딩 완료 여부와 시작 설정을 학습 진행 단일 행(learner_progress)에 함께 보관한다. */
@Singleton
class OnboardingRepositoryImpl
    @Inject
    constructor(
        private val progressDao: LearnerProgressDao,
    ) : OnboardingRepository {
        override fun observeOnboardingComplete(): Flow<Boolean> = progressDao.observe().map { it?.onboardingComplete ?: false }

        override suspend fun completeOnboarding(
            startingDifficulty: Int,
            dailyGoal: Int,
        ) {
            progressDao.insertDefaultIfAbsent(Difficulty.DEFAULT, SessionGoals.DAILY_GOAL_PROBLEMS)
            progressDao.completeOnboarding(
                difficulty = Difficulty.clamp(startingDifficulty),
                goal = dailyGoal,
            )
        }
    }
