package com.ddakpul.math.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.ddakpul.math.data.local.entity.ProblemEntity

/** 문제ID → 영역만 뽑아오는 경량 투영(리포트 집계용). */
data class ProblemAreaRow(
    val id: String,
    val area: String,
)

@Dao
interface ProblemDao {
    @Query("SELECT COUNT(*) FROM problem")
    suspend fun count(): Int

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(problems: List<ProblemEntity>)

    @Query("SELECT * FROM problem")
    suspend fun getAll(): List<ProblemEntity>

    @Query("SELECT * FROM problem WHERE id = :id")
    suspend fun getById(id: String): ProblemEntity?

    @Query("SELECT id, area FROM problem")
    suspend fun getAreaIndex(): List<ProblemAreaRow>
}
