package com.ddakpul.math.data.local.entity

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

// 추천은 매 문제마다 '최근 시도 N개'를, 통계는 전체를 시간순으로 읽는다 — 인덱스가 없으면
// 기록이 쌓일수록 풀스캔 + 임시 정렬 비용이 선형으로 늘어난다.
@Entity(
    tableName = "attempt",
    indices = [Index("timestamp"), Index("problemId"), Index(value = ["reviewMode", "timestamp"])],
)
data class AttemptEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val problemId: String,
    val isCorrect: Boolean,
    val timeSpentSec: Int,
    val timestamp: Long,
    /** 오답 노트 복습 재풀이 여부 — 추천 입력에서 걸러내되 통계에는 남긴다. */
    val reviewMode: Boolean = false,
)
