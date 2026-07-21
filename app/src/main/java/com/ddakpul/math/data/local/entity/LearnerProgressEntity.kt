package com.ddakpul.math.data.local.entity

import androidx.room.Entity
import androidx.room.PrimaryKey
import com.ddakpul.math.domain.model.SessionGoals

/** 학습 진행 상태 단일 행(현재 난이도 + 하루 목표 + 온보딩 완료 여부). 항상 [SINGLETON_ID] 한 행만 존재한다. */
@Entity(tableName = "learner_progress")
data class LearnerProgressEntity(
    @PrimaryKey val id: Int = SINGLETON_ID,
    val currentDifficulty: Int,
    val dailyGoal: Int = SessionGoals.DAILY_GOAL_PROBLEMS,
    /** 첫 실행 온보딩(소개·하루 목표·시작 난이도)을 마쳤는지. */
    val onboardingComplete: Boolean = false,
    /** 상위 난이도(기본 상한 위, 5~)를 열지 여부 — 설정 스위치. false면 [Difficulty.DEFAULT_OPEN_MAX]까지만. */
    val unlockAllLevels: Boolean = false,
    /** (미사용) 옛 이용권 만료 시각 컬럼 — DB 스키마 유지용. 유료화 재도입 시 재사용. */
    val premiumUntilMillis: Long = 0L,
) {
    companion object {
        const val SINGLETON_ID = 0
    }
}
