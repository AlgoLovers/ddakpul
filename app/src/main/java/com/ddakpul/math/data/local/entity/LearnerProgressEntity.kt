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
) {
    companion object {
        const val SINGLETON_ID = 0
    }
}
