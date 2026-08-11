package com.ddakpul.math.data.repository

import com.ddakpul.math.core.common.LocaleManagerCompat
import com.ddakpul.math.data.local.dao.ProblemDao
import com.ddakpul.math.data.local.seed.AssetProblemSource
import com.ddakpul.math.data.local.seed.ProblemCatalog
import com.ddakpul.math.data.mapper.toDomain
import com.ddakpul.math.data.mapper.toEntity
import com.ddakpul.math.domain.model.MathArea
import com.ddakpul.math.domain.model.Problem
import com.ddakpul.math.domain.model.ProblemGroup
import com.ddakpul.math.domain.repository.ProblemRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withContext
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

        /**
         * 시딩된 문제은행 캐시. 문제은행은 시딩 뒤 바뀌지 않는데, 캐시가 없으면 문제를 넘길 때마다
         * 1,100문항을 DB에서 읽어 JSON 3~5개씩 역직렬화한다(호출당 파싱 수천 회). 언어·버전이
         * 바뀌면 재시딩과 함께 비운다.
         */
        @Volatile
        private var cachedGroups: List<ProblemGroup>? = null

        private suspend fun ensureSeeded() {
            // 수제 카탈로그는 한국어 전용이다 — 영어 모드에 섞으면 읽지 못하는 문제가
            // 12% 확률로 나온다(2026-08 QA). 영어에서는 이중언어인 생성 문항만 낸다.
            val handMade = if (assetProblemSource.langTag == LocaleManagerCompat.KOREAN) ProblemCatalog.problems else emptyList()
            val all = handMade + assetProblemSource.problems
            val lang = assetProblemSource.langTag
            val version = AssetProblemSource.CONTENT_VERSION
            // 문항 수가 같아도 (1) 언어가 바뀌었거나(앱 내 언어 토글) (2) 내용 버전이 올랐으면
            // (기존 문제의 난이도·풀이 등 수정) 문제은행을 새로 시딩한다.
            // 문제 id는 언어·버전과 무관하게 동일해 학습 기록(시도·진도)은 그대로 유지된다.
            if (isSeeded(all.size, lang, version)) return
            seedMutex.withLock {
                // 락을 기다리는 사이 다른 코루틴이 이미 시딩했을 수 있으니 다시 확인한다.
                if (isSeeded(all.size, lang, version)) return
                problemDao.replaceAll(all.map { it.toEntity() })
                assetProblemSource.seededLang = lang
                assetProblemSource.seededContentVersion = version
                cachedGroups = null
            }
        }

        /** 이미 현재 문항 수·언어·내용 버전으로 시딩돼 있으면 true(재시딩 불필요). */
        private suspend fun isSeeded(
            expectedCount: Int,
            lang: String,
            version: Int,
        ): Boolean =
            problemDao.count() == expectedCount &&
                assetProblemSource.seededLang == lang &&
                assetProblemSource.seededContentVersion == version

        // 파싱·그룹핑은 CPU 작업이라 호출자(대개 viewModelScope = Main)에서 돌면 안 된다.
        override suspend fun getAllGroups(): List<ProblemGroup> =
            withContext(Dispatchers.IO) {
                ensureSeeded()
                cachedGroups ?: problemDao
                    .getAll()
                    .map { it.toDomain() }
                    .groupBy { it.groupId }
                    .map { (groupId, problems) -> problems.toGroup(groupId) }
                    .also { cachedGroups = it }
            }

        override suspend fun getProblem(id: String): Problem? =
            withContext(Dispatchers.IO) {
                ensureSeeded()
                problemDao.getById(id)?.toDomain()
            }

        override suspend fun areaByProblemId(): Map<String, MathArea> =
            withContext(Dispatchers.IO) {
                ensureSeeded()
                problemDao.getAreaIndex().associate { it.id to MathArea.valueOf(it.area) }
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
