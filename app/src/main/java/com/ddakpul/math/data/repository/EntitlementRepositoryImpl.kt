package com.ddakpul.math.data.repository

import com.ddakpul.math.core.common.MILLIS_PER_DAY
import com.ddakpul.math.data.local.dao.LearnerProgressDao
import com.ddakpul.math.data.local.entity.LearnerProgressEntity
import com.ddakpul.math.domain.model.Difficulty
import com.ddakpul.math.domain.model.Entitlement
import com.ddakpul.math.domain.repository.EntitlementRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

/** 이용권 만료 시각을 학습 진행 단일 행(learner_progress)에 함께 보관한다. */
@Singleton
class EntitlementRepositoryImpl
    @Inject
    constructor(
        private val progressDao: LearnerProgressDao,
    ) : EntitlementRepository {
        override fun observeEntitlement(): Flow<Entitlement> = progressDao.observe().map { Entitlement(it?.premiumUntilMillis ?: 0L) }

        override suspend fun getEntitlement(): Entitlement = Entitlement(progressDao.get()?.premiumUntilMillis ?: 0L)

        override suspend fun grantPass(
            durationDays: Int,
            nowMillis: Long,
        ) {
            val current = progressDao.get()
            val base = maxOf(nowMillis, current?.premiumUntilMillis ?: 0L)
            val newUntil = base + durationDays.toLong() * MILLIS_PER_DAY
            progressDao.upsert(
                (current ?: LearnerProgressEntity(currentDifficulty = Difficulty.DEFAULT)).copy(premiumUntilMillis = newUntil),
            )
        }
    }
