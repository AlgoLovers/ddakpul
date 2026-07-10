package com.ddakpul.math.data.local.seed

import android.content.Context
import dagger.hilt.android.qualifiers.ApplicationContext
import javax.inject.Inject
import javax.inject.Singleton

/** assets에 내장된 생성 문제은행 로더. 최초 접근 시 한 번만 파싱해 캐시한다. */
@Singleton
class AssetProblemSource
    @Inject
    constructor(
        @ApplicationContext private val context: Context,
    ) {
        val problems by lazy {
            context.assets
                .open(FILE_NAME)
                .bufferedReader()
                .use { it.readText() }
                .let(::parseAssetProblems)
        }

        companion object {
            const val FILE_NAME = "problems_generated.json"
        }
    }
