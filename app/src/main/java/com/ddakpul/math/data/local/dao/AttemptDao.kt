package com.ddakpul.math.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.Query
import com.ddakpul.math.data.local.entity.AttemptEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface AttemptDao {
    @Insert
    suspend fun insert(attempt: AttemptEntity)

    /**
     * 최신 시도부터 [limit]개(추천 입력). 호출부에서 시간 오름차순으로 뒤집어 사용한다.
     * 오답 노트 복습 재풀이(reviewMode)는 제외한다 — 복습 성적이 난이도 승급/강등을 흔들지 않게.
     */
    @Query("SELECT * FROM attempt WHERE reviewMode = 0 ORDER BY timestamp DESC, id DESC LIMIT :limit")
    suspend fun recent(limit: Int): List<AttemptEntity>

    @Query("SELECT * FROM attempt ORDER BY timestamp ASC, id ASC")
    fun observeAll(): Flow<List<AttemptEntity>>

    @Query("SELECT * FROM attempt ORDER BY timestamp ASC, id ASC")
    suspend fun getAll(): List<AttemptEntity>

    @Query("DELETE FROM attempt")
    suspend fun deleteAll()
}
