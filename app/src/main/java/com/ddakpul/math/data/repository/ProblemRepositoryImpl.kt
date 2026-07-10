package com.ddakpul.math.data.repository

import com.ddakpul.math.data.local.dao.ProblemDao
import com.ddakpul.math.data.local.seed.ProblemCatalog
import com.ddakpul.math.data.mapper.toDomain
import com.ddakpul.math.data.mapper.toEntity
import com.ddakpul.math.domain.model.MathArea
import com.ddakpul.math.domain.model.Problem
import com.ddakpul.math.domain.model.ProblemGroup
import com.ddakpul.math.domain.repository.ProblemRepository
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Room 기반 문제은행. 최초 접근 시 내장 [ProblemCatalog]를 한 번 시딩한다(오프라인 우선).
 */
@Singleton
class ProblemRepositoryImpl
    @Inject
    constructor(
        private val problemDao: ProblemDao,
    ) : ProblemRepository {
        private val seedMutex = Mutex()

        private suspend fun ensureSeeded() {
            if (problemDao.count() > 0) return
            seedMutex.withLock {
                // 락을 기다리는 사이 다른 코루틴이 이미 시딩했을 수 있으니 다시 확인한다.
                if (problemDao.count() > 0) return
                problemDao.insertAll(ProblemCatalog.problems.map { it.toEntity() })
            }
        }

        override suspend fun getAllGroups(): List<ProblemGroup> {
            ensureSeeded()
            return problemDao
                .getAll()
                .map { it.toDomain() }
                .groupBy { it.groupId }
                .map { (groupId, problems) -> problems.toGroup(groupId) }
        }

        override suspend fun getProblem(id: String): Problem? {
            ensureSeeded()
            return problemDao.getById(id)?.toDomain()
        }

        override suspend fun areaByProblemId(): Map<String, MathArea> {
            ensureSeeded()
            return problemDao.getAreaIndex().associate { it.id to MathArea.valueOf(it.area) }
        }

        private fun List<Problem>.toGroup(groupId: String): ProblemGroup {
            val representative = first()
            return ProblemGroup(
                id = groupId,
                area = representative.area,
                difficulty = representative.difficulty,
                conceptTags = flatMap { it.conceptTags }.distinct(),
                problems = this,
            )
        }
    }
