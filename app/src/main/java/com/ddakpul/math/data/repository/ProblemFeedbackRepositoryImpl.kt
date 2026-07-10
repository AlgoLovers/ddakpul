package com.ddakpul.math.data.repository

import com.ddakpul.math.data.local.dao.ExcludedProblemDao
import com.ddakpul.math.data.local.entity.ExcludedProblemEntity
import com.ddakpul.math.domain.model.ExcludedProblem
import com.ddakpul.math.domain.repository.ProblemFeedbackRepository
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class ProblemFeedbackRepositoryImpl
    @Inject
    constructor(
        private val excludedProblemDao: ExcludedProblemDao,
    ) : ProblemFeedbackRepository {
        override suspend fun exclude(
            problemId: String,
            reason: String?,
            timestampMillis: Long,
        ) {
            excludedProblemDao.insert(
                ExcludedProblemEntity(
                    problemId = problemId,
                    reason = reason,
                    excludedAt = timestampMillis,
                ),
            )
        }

        override suspend fun getExcludedIds(): Set<String> = excludedProblemDao.getIds().toSet()

        override suspend fun getAllExclusions(): List<ExcludedProblem> =
            excludedProblemDao.getAll().map {
                ExcludedProblem(
                    problemId = it.problemId,
                    reason = it.reason,
                    excludedAtMillis = it.excludedAt,
                )
            }

        override fun observeExcludedCount(): Flow<Int> = excludedProblemDao.observeCount()
    }
