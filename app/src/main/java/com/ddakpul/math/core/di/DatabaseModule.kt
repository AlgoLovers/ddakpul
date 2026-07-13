package com.ddakpul.math.core.di

import android.content.Context
import androidx.room.Room
import com.ddakpul.math.data.local.DdakPulDatabase
import com.ddakpul.math.data.local.MIGRATION_1_2
import com.ddakpul.math.data.local.MIGRATION_2_3
import com.ddakpul.math.data.local.MIGRATION_3_4
import com.ddakpul.math.data.local.MIGRATION_4_5
import com.ddakpul.math.data.local.MIGRATION_5_6
import com.ddakpul.math.data.local.dao.AttemptDao
import com.ddakpul.math.data.local.dao.ExcludedProblemDao
import com.ddakpul.math.data.local.dao.LearnerProgressDao
import com.ddakpul.math.data.local.dao.ProblemDao
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {
    private const val DATABASE_NAME = "ddakpul.db"

    @Provides
    @Singleton
    fun provideDatabase(
        @ApplicationContext context: Context,
    ): DdakPulDatabase =
        Room
            .databaseBuilder(context, DdakPulDatabase::class.java, DATABASE_NAME)
            .addMigrations(MIGRATION_1_2, MIGRATION_2_3, MIGRATION_3_4, MIGRATION_4_5, MIGRATION_5_6)
            .build()

    @Provides
    fun provideProblemDao(database: DdakPulDatabase): ProblemDao = database.problemDao()

    @Provides
    fun provideAttemptDao(database: DdakPulDatabase): AttemptDao = database.attemptDao()

    @Provides
    fun provideLearnerProgressDao(database: DdakPulDatabase): LearnerProgressDao = database.learnerProgressDao()

    @Provides
    fun provideExcludedProblemDao(database: DdakPulDatabase): ExcludedProblemDao = database.excludedProblemDao()
}
