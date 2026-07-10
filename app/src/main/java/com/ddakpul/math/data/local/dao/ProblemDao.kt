package com.ddakpul.math.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Transaction
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

    @Query("DELETE FROM problem")
    suspend fun deleteAll()

    /** 문제은행 전체 교체 — 앱 업데이트로 문항이 추가/삭제돼도 은행이 정확히 일치하게. */
    @Transaction
    suspend fun replaceAll(problems: List<ProblemEntity>) {
        deleteAll()
        insertAll(problems)
    }

    @Query("SELECT * FROM problem")
    suspend fun getAll(): List<ProblemEntity>

    @Query("SELECT * FROM problem WHERE id = :id")
    suspend fun getById(id: String): ProblemEntity?

    @Query("SELECT id, area FROM problem")
    suspend fun getAreaIndex(): List<ProblemAreaRow>
}
