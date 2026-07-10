package com.ddakpul.math.data.local

import androidx.room.migration.Migration
import androidx.sqlite.db.SupportSQLiteDatabase
import com.ddakpul.math.domain.model.SessionGoals

/** v1 → v2: 하루 목표(dailyGoal) 컬럼 추가 — 아이가 스스로 목표를 정할 수 있게. */
val MIGRATION_1_2 =
    object : Migration(1, 2) {
        override fun migrate(db: SupportSQLiteDatabase) {
            db.execSQL(
                "ALTER TABLE learner_progress " +
                    "ADD COLUMN dailyGoal INTEGER NOT NULL DEFAULT ${SessionGoals.DAILY_GOAL_PROBLEMS}",
            )
        }
    }
