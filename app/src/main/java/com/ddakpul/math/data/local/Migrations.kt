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

/**
 * v2 → v3: 학년(grade)·학기(semester) 컬럼 제거 — 난이도(1~5)가 유일한 수준 축.
 * 문제 테이블은 내장 카탈로그에서 다시 시딩되므로 통째로 재생성해도 데이터 손실이 없다.
 * (풀이 기록 attempt 테이블은 건드리지 않는다.)
 */
val MIGRATION_2_3 =
    object : Migration(2, 3) {
        override fun migrate(db: SupportSQLiteDatabase) {
            db.execSQL("DROP TABLE IF EXISTS problem")
            db.execSQL(
                "CREATE TABLE IF NOT EXISTS problem (" +
                    "id TEXT NOT NULL, " +
                    "area TEXT NOT NULL, " +
                    "conceptTagsJson TEXT NOT NULL, " +
                    "difficulty INTEGER NOT NULL, " +
                    "groupId TEXT NOT NULL, " +
                    "statement TEXT NOT NULL, " +
                    "choicesJson TEXT NOT NULL, " +
                    "correctChoiceIndex INTEGER NOT NULL, " +
                    "explanation TEXT, " +
                    "mistakesJson TEXT NOT NULL, " +
                    "PRIMARY KEY(id))",
            )
        }
    }

/** v3 → v4: 도형 지시서(figureJson) 컬럼 추가 — 그림으로 설명하는 문제 지원. */
val MIGRATION_3_4 =
    object : Migration(3, 4) {
        override fun migrate(db: SupportSQLiteDatabase) {
            db.execSQL("ALTER TABLE problem ADD COLUMN figureJson TEXT")
        }
    }
