package com.ddakpul.math.data.repository

import com.ddakpul.math.data.local.dao.ProblemDao
import com.ddakpul.math.data.local.seed.AssetProblemSource
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
 * Room 기반 문제은행. 손으로 만든 [ProblemCatalog]와 생성 파이프라인 산출물
 * ([AssetProblemSource])을 합쳐 시딩한다(오프라인 우선). 앱 업데이트로 문항 수가
 * 달라지면 은행 전체를 교체해 추가·삭제를 정확히 반영한다.
 */
@Singleton
class ProblemRepositoryImpl
    @Inject
    constructor(
        private val problemDao: ProblemDao,
        private val assetProblemSource: AssetProblemSource,
    ) : ProblemRepository {
        private val seedMutex = Mutex()

        private suspend fun ensureSeeded() {
            val all = ProblemCatalog.problems + assetProblemSource.problems
            val lang = assetProblemSource.langTag
            // 문항 수가 같아도 언어가 바뀌었으면(앱 내 언어 토글) 문제은행 텍스트를 새로 시딩한다.
            // 문제 id는 언어와 무관하게 동일해 학습 기록(시도·진도)은 그대로 유지된다.
            if (problemDao.count() == all.size && assetProblemSource.seededLang == lang) return
            seedMutex.withLock {
                // 락을 기다리는 사이 다른 코루틴이 이미 시딩했을 수 있으니 다시 확인한다.
                if (problemDao.count() == all.size && assetProblemSource.seededLang == lang) return
                problemDao.replaceAll(all.map { it.toEntity() })
                assetProblemSource.seededLang = lang
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
