package com.ddakpul.math.data.local

import androidx.room.Database
import androidx.room.RoomDatabase
import com.ddakpul.math.data.local.dao.AttemptDao
import com.ddakpul.math.data.local.dao.LearnerProgressDao
import com.ddakpul.math.data.local.dao.ProblemDao
import com.ddakpul.math.data.local.entity.AttemptEntity
import com.ddakpul.math.data.local.entity.LearnerProgressEntity
import com.ddakpul.math.data.local.entity.ProblemEntity

@Database(
    entities = [
        ProblemEntity::class,
        AttemptEntity::class,
        LearnerProgressEntity::class,
    ],
    version = 3,
    exportSchema = false,
)
abstract class DdakPulDatabase : RoomDatabase() {
    abstract fun problemDao(): ProblemDao

    abstract fun attemptDao(): AttemptDao

    abstract fun learnerProgressDao(): LearnerProgressDao
}
