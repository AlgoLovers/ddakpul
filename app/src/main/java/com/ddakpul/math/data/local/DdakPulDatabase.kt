package com.ddakpul.math.data.local

import androidx.room.Database
import androidx.room.RoomDatabase
import com.ddakpul.math.data.local.dao.AttemptDao
import com.ddakpul.math.data.local.dao.ExcludedProblemDao
import com.ddakpul.math.data.local.dao.LearnerProgressDao
import com.ddakpul.math.data.local.dao.ProblemDao
import com.ddakpul.math.data.local.entity.AttemptEntity
import com.ddakpul.math.data.local.entity.ExcludedProblemEntity
import com.ddakpul.math.data.local.entity.LearnerProgressEntity
import com.ddakpul.math.data.local.entity.ProblemEntity

@Database(
    entities = [
        ProblemEntity::class,
        AttemptEntity::class,
        LearnerProgressEntity::class,
        ExcludedProblemEntity::class,
    ],
    version = 6,
    exportSchema = false,
)
abstract class DdakPulDatabase : RoomDatabase() {
    abstract fun problemDao(): ProblemDao

    abstract fun attemptDao(): AttemptDao

    abstract fun learnerProgressDao(): LearnerProgressDao

    abstract fun excludedProblemDao(): ExcludedProblemDao
}
