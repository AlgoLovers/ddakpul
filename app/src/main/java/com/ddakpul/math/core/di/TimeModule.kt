package com.ddakpul.math.core.di

import com.ddakpul.math.data.time.SystemClock
import com.ddakpul.math.domain.time.Clock
import dagger.Binds
import dagger.Module
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent

/** 시간 공급자 바인딩. 테스트는 이 모듈을 대체해 고정 시각 [Clock]을 넣는다. */
@Module
@InstallIn(SingletonComponent::class)
abstract class TimeModule {
    @Binds
    abstract fun bindClock(impl: SystemClock): Clock
}
