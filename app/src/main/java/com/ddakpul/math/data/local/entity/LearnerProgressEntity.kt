package com.ddakpul.math.data.local.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

/** 학습 진행 상태 단일 행(현재 난이도). 항상 [SINGLETON_ID] 한 행만 존재한다. */
@Entity(tableName = "learner_progress")
data class LearnerProgressEntity(
    @PrimaryKey val id: Int = SINGLETON_ID,
    val currentDifficulty: Int,
) {
    companion object {
        const val SINGLETON_ID = 0
    }
}
