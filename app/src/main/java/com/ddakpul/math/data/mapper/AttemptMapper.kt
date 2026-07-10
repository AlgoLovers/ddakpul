package com.ddakpul.math.data.mapper

import com.ddakpul.math.data.local.entity.AttemptEntity
import com.ddakpul.math.domain.model.Attempt

fun AttemptEntity.toDomain(): Attempt =
    Attempt(
        problemId = problemId,
        isCorrect = isCorrect,
        timeSpentSec = timeSpentSec,
        timestamp = timestamp,
    )

fun Attempt.toEntity(): AttemptEntity =
    AttemptEntity(
        problemId = problemId,
        isCorrect = isCorrect,
        timeSpentSec = timeSpentSec,
        timestamp = timestamp,
    )
