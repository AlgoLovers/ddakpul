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
)
