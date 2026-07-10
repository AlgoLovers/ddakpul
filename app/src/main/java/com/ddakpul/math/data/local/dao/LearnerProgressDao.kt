package com.ddakpul.math.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.ddakpul.math.data.local.entity.LearnerProgressEntity

@Dao
interface LearnerProgressDao {
    @Query("SELECT * FROM learner_progress WHERE id = ${LearnerProgressEntity.SINGLETON_ID}")
    suspend fun get(): LearnerProgressEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(entity: LearnerProgressEntity)

    @Query("DELETE FROM learner_progress")
    suspend fun deleteAll()
}
