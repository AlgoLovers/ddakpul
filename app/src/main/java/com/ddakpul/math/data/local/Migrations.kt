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

/** v4 → v5: "별로예요" 제외 문제 테이블 — 제외한 문제는 추천·학습지에서 다시 나오지 않는다. */
val MIGRATION_4_5 =
    object : Migration(4, 5) {
        override fun migrate(db: SupportSQLiteDatabase) {
            db.execSQL(
                "CREATE TABLE IF NOT EXISTS excluded_problem (" +
                    "problemId TEXT NOT NULL, " +
                    "reason TEXT, " +
                    "excludedAt INTEGER NOT NULL, " +
                    "PRIMARY KEY(problemId))",
            )
        }
    }

/** v5 → v6: 온보딩 완료 여부(onboardingComplete) 컬럼 추가 — 첫 실행 안내를 한 번만 보여주기 위해. */
val MIGRATION_5_6 =
    object : Migration(5, 6) {
        override fun migrate(db: SupportSQLiteDatabase) {
            db.execSQL(
                "ALTER TABLE learner_progress ADD COLUMN onboardingComplete INTEGER NOT NULL DEFAULT 0",
            )
        }
    }

/** v6 → v7: 이용권 만료 시각(premiumUntilMillis) 컬럼 추가 — 기간제 프리미엄 이용권 상태 보관. */
val MIGRATION_6_7 =
    object : Migration(6, 7) {
        override fun migrate(db: SupportSQLiteDatabase) {
            db.execSQL(
                "ALTER TABLE learner_progress ADD COLUMN premiumUntilMillis INTEGER NOT NULL DEFAULT 0",
            )
        }
    }

val MIGRATION_7_8 =
    object : Migration(7, 8) {
        override fun migrate(db: SupportSQLiteDatabase) {
            db.execSQL("ALTER TABLE problems ADD COLUMN detailedExplanation TEXT")
            // problems는 순수 시드 데이터 — 비워서 다음 접근 때 최신 콘텐츠(2차 풀이 포함)로 강제 재시딩.
            db.execSQL("DELETE FROM problems")
        }
    }
