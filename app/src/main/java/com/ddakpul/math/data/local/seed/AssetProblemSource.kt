package com.ddakpul.math.data.local.seed

import android.content.Context
import com.ddakpul.math.core.common.LocaleManagerCompat
import dagger.hilt.android.qualifiers.ApplicationContext
import javax.inject.Inject
import javax.inject.Singleton

/**
 * assets에 내장된 생성 문제은행 로더. 최초 접근 시 한 번만 파싱해 캐시한다.
 *
 * 다국어: 앱 언어가 영어면 영어 뱅크(problems_generated_en.json)를 덧씌운다 — 아직 영어로
 * 변환된 계열만 영어로 나오고, 나머지는 한국어로 폴백(점진적 i18n). 문제 id로 1:1 매칭한다.
 * 언어는 [LocaleManagerCompat]가 정하는 유효 언어를 따른다(앱 내 토글 > 시스템).
 */
@Singleton
class AssetProblemSource
    @Inject
    constructor(
        @ApplicationContext private val context: Context,
    ) {
        /** 지금 프로세스가 문제를 읽어 온 언어("ko"/"en"). 재시딩이 시딩 언어와 비교하는 값. */
        val langTag: String
            get() = LocaleManagerCompat.currentLang(context)

        val problems by lazy {
            val ko = parseAssetProblems(readAsset(FILE_NAME))
            if (langTag != LocaleManagerCompat.ENGLISH) return@lazy ko
            val en = runCatching { parseAssetProblems(readAsset(FILE_NAME_EN)) }.getOrDefault(emptyList())
            if (en.isEmpty()) return@lazy ko
            val enById = en.associateBy { it.id }
            ko.map { enById[it.id] ?: it } // 영어가 있으면 영어, 없으면 한국어 폴백
        }

        /** DB에 마지막으로 시딩한 언어. 앱 언어가 이와 다르면 문제은행을 다시 시딩해야 한다. */
        var seededLang: String?
            get() = prefs().getString(KEY_SEEDED_LANG, null)
            set(value) {
                prefs().edit().putString(KEY_SEEDED_LANG, value).apply()
            }

        private fun prefs() = context.getSharedPreferences(PREF, Context.MODE_PRIVATE)

        private fun readAsset(name: String): String =
            context.assets
                .open(name)
                .bufferedReader()
                .use { it.readText() }

        companion object {
            const val FILE_NAME = "problems_generated.json"
            const val FILE_NAME_EN = "problems_generated_en.json"
            private const val PREF = "ddakpul_seed"
            private const val KEY_SEEDED_LANG = "seeded_lang"
        }
    }
