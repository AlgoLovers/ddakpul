package com.ddakpul.math.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.ddakpul.math.data.local.entity.ExcludedProblemEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface ExcludedProblemDao {
    /** 같은 문제를 다시 제외해도 오류 없이 최신 기록으로 덮어쓴다. */
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(entity: ExcludedProblemEntity)

    @Query("SELECT problemId FROM excluded_problem")
    suspend fun getIds(): List<String>

    @Query("SELECT * FROM excluded_problem ORDER BY excludedAt ASC")
    suspend fun getAll(): List<ExcludedProblemEntity>

    @Query("SELECT COUNT(*) FROM excluded_problem")
    fun observeCount(): Flow<Int>
}
