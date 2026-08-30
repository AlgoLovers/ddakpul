package com.ddakpul.math.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.ddakpul.math.data.local.entity.LearnerProgressEntity
import kotlinx.coroutines.flow.Flow

/**
 * 학습 진행 단일 행에 대한 접근. 값을 바꿀 때는 행 전체를 다시 쓰지 않고 **필드별 UPDATE**를
 * 쓴다 — 읽고-고쳐-쓰기로 하면 난이도 저장과 하루 목표 저장이 겹칠 때 서로의 값을 덮어쓴다.
 * (난이도는 문제를 넘길 때마다 자동으로 저장되므로 겹칠 창이 늘 열려 있다.)
 */
@Dao
interface LearnerProgressDao {
    @Query("SELECT * FROM learner_progress WHERE id = ${LearnerProgressEntity.SINGLETON_ID}")
    suspend fun get(): LearnerProgressEntity?

    @Query("SELECT * FROM learner_progress WHERE id = ${LearnerProgressEntity.SINGLETON_ID}")
    fun observe(): Flow<LearnerProgressEntity?>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(entity: LearnerProgressEntity)

    /** 아직 행이 없을 때만 기본값 행을 만든다 — 필드별 UPDATE의 선행 단계. 있으면 아무것도 하지 않는다. */
    @Query(
        "INSERT OR IGNORE INTO learner_progress " +
            "(id, currentDifficulty, dailyGoal, onboardingComplete, unlockAllLevels, premiumUntilMillis) " +
            "VALUES (${LearnerProgressEntity.SINGLETON_ID}, :defaultDifficulty, :defaultDailyGoal, 0, 0, 0)",
    )
    suspend fun insertDefaultIfAbsent(
        defaultDifficulty: Int,
        defaultDailyGoal: Int,
    )

    @Query("UPDATE learner_progress SET currentDifficulty = :difficulty WHERE id = ${LearnerProgressEntity.SINGLETON_ID}")
    suspend fun updateCurrentDifficulty(difficulty: Int)

    @Query("UPDATE learner_progress SET dailyGoal = :goal WHERE id = ${LearnerProgressEntity.SINGLETON_ID}")
    suspend fun updateDailyGoal(goal: Int)

    @Query("UPDATE learner_progress SET unlockAllLevels = :enabled WHERE id = ${LearnerProgressEntity.SINGLETON_ID}")
    suspend fun updateUnlockAllLevels(enabled: Boolean)

    /** 온보딩 완료 — 시작 난이도·하루 목표·완료 표시를 한 번에 확정한다. */
    @Query(
        "UPDATE learner_progress SET currentDifficulty = :difficulty, dailyGoal = :goal, onboardingComplete = 1 " +
            "WHERE id = ${LearnerProgressEntity.SINGLETON_ID}",
    )
    suspend fun completeOnboarding(
        difficulty: Int,
        goal: Int,
    )

    @Query("DELETE FROM learner_progress")
    suspend fun deleteAll()
}
