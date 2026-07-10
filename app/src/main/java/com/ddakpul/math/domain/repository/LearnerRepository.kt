package com.ddakpul.math.domain.repository

import com.ddakpul.math.domain.model.Attempt
import com.ddakpul.math.domain.model.LearnerState
import kotlinx.coroutines.flow.Flow

/** 학습자 진행 상태(현재 난이도)와 풀이 기록의 저장소. */
interface LearnerRepository {
    /** 추천 입력으로 쓸 현재 학습자 상태(현재 난이도 + 최근 시도)를 구성해 돌려준다. */
    suspend fun getLearnerState(): LearnerState

    suspend fun getCurrentDifficulty(): Int

    suspend fun recordAttempt(attempt: Attempt)

    suspend fun setCurrentDifficulty(difficulty: Int)

    /** 리포트용 전체 시도 스트림(시간 오름차순). */
    fun observeAttempts(): Flow<List<Attempt>>

    /** 복습 스케줄 재생용 전체 시도(시간 오름차순). */
    suspend fun getAllAttempts(): List<Attempt>

    /** 아이가 스스로 정한 하루 목표 문항 수(미설정이면 기본값). */
    fun observeDailyGoal(): Flow<Int>

    suspend fun setDailyGoal(goal: Int)

    /** 모든 풀이 기록과 난이도를 초기화한다(하루 목표는 유지). */
    suspend fun resetProgress()
}
