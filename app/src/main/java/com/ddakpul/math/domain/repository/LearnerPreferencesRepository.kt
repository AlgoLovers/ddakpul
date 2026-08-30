package com.ddakpul.math.domain.repository

import kotlinx.coroutines.flow.Flow

/**
 * 학습자가 고른 설정의 저장소 — 하루 목표, 상위 난이도 열기.
 * 학습 **기록**([LearnerRepository])과 분리한다: 기록은 앱이 쌓는 것이고 이쪽은 사람이 정하는
 * 것이라 수명이 다르다(진도 초기화가 설정을 지우지 않는 이유). 설정만 필요한 화면이
 * 풀이 기록 API까지 함께 들고 다니지 않게 하는 목적도 있다.
 */
interface LearnerPreferencesRepository {
    /** 아이가 스스로 정한 하루 목표 문항 수(미설정이면 기본값). */
    fun observeDailyGoal(): Flow<Int>

    suspend fun setDailyGoal(goal: Int)

    /** 상위 난이도(기본 상한 위) 열기 설정 — 켜면 모든 난이도가 추천에 나온다. */
    fun observeUnlockAllLevels(): Flow<Boolean>

    suspend fun getUnlockAllLevels(): Boolean

    suspend fun setUnlockAllLevels(enabled: Boolean)
}
