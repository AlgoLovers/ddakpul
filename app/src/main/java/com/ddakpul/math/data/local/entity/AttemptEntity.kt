package com.ddakpul.math.data.local.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "attempt")
data class AttemptEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val problemId: String,
    val isCorrect: Boolean,
    val timeSpentSec: Int,
    val timestamp: Long,
    /** 오답 노트 복습 재풀이 여부 — 추천 입력에서 걸러내되 통계에는 남긴다. */
    val reviewMode: Boolean = false,
)
