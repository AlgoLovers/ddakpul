package com.ddakpul.math.core.di

import com.ddakpul.math.data.repository.LearnerRepositoryImpl
import com.ddakpul.math.data.repository.ProblemRepositoryImpl
import com.ddakpul.math.domain.repository.LearnerRepository
import com.ddakpul.math.domain.repository.ProblemRepository
import dagger.Binds
import dagger.Module
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent

@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {
    @Binds
    abstract fun bindProblemRepository(impl: ProblemRepositoryImpl): ProblemRepository

    @Binds
    abstract fun bindLearnerRepository(impl: LearnerRepositoryImpl): LearnerRepository
}
