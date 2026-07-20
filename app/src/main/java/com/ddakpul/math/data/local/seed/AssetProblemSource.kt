package com.ddakpul.math.data.local.seed

import android.content.Context
import com.ddakpul.math.core.common.LocaleManagerCompat
import com.ddakpul.math.domain.model.Problem
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

        val problems by lazy { multipleChoiceBank() + dissectionBank() }

        /** 4지선다 문제은행(ko + 영어 오버레이). */
        private fun multipleChoiceBank(): List<Problem> {
            val ko = parseAssetProblems(readAsset(FILE_NAME))
            if (langTag != LocaleManagerCompat.ENGLISH) return ko
            val en = runCatching { parseAssetProblems(readAsset(FILE_NAME_EN)) }.getOrDefault(emptyList())
            if (en.isEmpty()) return ko
            val enById = en.associateBy { it.id }
            return ko.map { enById[it.id] ?: it } // 영어가 있으면 영어, 없으면 한국어 폴백
        }

        /** 격자 등분 퍼즐(구성형) — 문장은 현재 언어로 즉석 생성하므로 언어 오버레이가 필요 없다. */
        private fun dissectionBank(): List<Problem> =
            runCatching {
                parseDissectionProblems(readAsset(FILE_NAME_DISSECTION), langTag == LocaleManagerCompat.ENGLISH)
            }.getOrDefault(emptyList())

        /** DB에 마지막으로 시딩한 언어. 앱 언어가 이와 다르면 문제은행을 다시 시딩해야 한다. */
        var seededLang: String?
            get() = prefs().getString(KEY_SEEDED_LANG, null)
            set(value) {
                prefs().edit().putString(KEY_SEEDED_LANG, value).apply()
            }

        /**
         * DB에 마지막으로 시딩한 문제 '내용' 버전. 문항 수가 그대로여도 기존 문제의 난이도·풀이·코드
         * 같은 값이 바뀌면 이 값이 [CONTENT_VERSION]과 어긋나 재시딩된다(문제 id는 불변이라 학습 기록 유지).
         */
        var seededContentVersion: Int
            get() = prefs().getInt(KEY_SEEDED_VERSION, 0)
            set(value) {
                prefs().edit().putInt(KEY_SEEDED_VERSION, value).apply()
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
            const val FILE_NAME_DISSECTION = "problems_dissection.json"

            /**
             * 문제은행 '내용' 버전. 문항 수가 그대로여도 기존 문제의 난이도·풀이·코드 등이 바뀌면
             * 이 값을 올린다 → 기존 설치가 다음 실행 때 재시딩된다.
             * v2: 점화식 4형제(gen-recur-1~4) 난이도 10→5 재조정. v3: 격자 등분 퍼즐 편입.
             * v4: 물 붓기 퍼즐(gen-waterjug, 변화와관계 난9) 5문항 신규 — CHANGE d9 유형 다양성 보강.
             */
            const val CONTENT_VERSION = 4
            private const val PREF = "ddakpul_seed"
            private const val KEY_SEEDED_LANG = "seeded_lang"
            private const val KEY_SEEDED_VERSION = "seeded_content_version"
        }
    }
