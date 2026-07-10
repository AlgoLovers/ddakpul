package com.ddakpul.math.data.local.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "excluded_problem")
data class ExcludedProblemEntity(
    @PrimaryKey val problemId: String,
    val reason: String?,
    val excludedAt: Long,
)
