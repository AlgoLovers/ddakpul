package com.ddakpul.math.core.common

import android.app.LocaleManager
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.LocaleList
import java.util.Locale

/**
 * 앱 안에서 UI 언어를 바꾸는 자체 로케일 스위처(API 26+ 동작, appcompat 불필요).
 *
 * - 선택은 SharedPreferences에 저장한다(진실의 원천). null이면 시스템 언어를 따른다.
 * - [wrap]을 Application/Activity의 `attachBaseContext`에서 호출해 저장된 언어를 강제한다.
 * - [apply]는 언어를 저장하고, 33+에서는 시스템 per-app 로케일과도 동기화한 뒤,
 *   **프로세스를 완전히 재시작**한다. 문제 콘텐츠가 언어에 따라 DB에 시딩되고
 *   [com.ddakpul.math.data.local.seed.AssetProblemSource]가 lazy 캐시라, 재시작해야
 *   UI 문자열뿐 아니라 문제 콘텐츠까지 새 언어로 바뀐다.
 */
object LocaleManagerCompat {
    private const val PREF = "ddakpul_locale"
    private const val KEY_LANG = "app_lang"

    /** 지원 언어 태그. UI 토글이 고르는 값이자, 재시딩이 비교하는 값이다. */
    const val KOREAN = "ko"
    const val ENGLISH = "en"
    val SUPPORTED = listOf(KOREAN, ENGLISH)

    private fun prefs(context: Context) = context.getSharedPreferences(PREF, Context.MODE_PRIVATE)

    /** 사용자가 명시적으로 고른 언어 태그. null이면 '시스템 따름'. */
    fun storedTag(context: Context): String? = prefs(context).getString(KEY_LANG, null)

    /**
     * 지금 화면에 실제로 적용될 언어("ko"/"en"). 저장값이 있으면 그것을, 없으면 시스템 언어를
     * 지원 목록에 맞춰 해석한다(영어권이면 en, 그 외 ko). 문제 재시딩·토글 표시의 기준.
     */
    fun currentLang(context: Context): String {
        storedTag(context)?.let { return it }
        val sys =
            context.resources.configuration.locales[0]
                .language
        return if (sys == ENGLISH) ENGLISH else KOREAN
    }

    /** 저장된 언어를 [base] 컨텍스트에 입혀 돌려준다. 저장값이 없으면 그대로 둔다(시스템 따름). */
    fun wrap(base: Context): Context {
        val tag = storedTag(base) ?: return base
        val locale = Locale.forLanguageTag(tag)
        Locale.setDefault(locale)
        val config = base.resources.configuration
        config.setLocale(locale)
        config.setLocales(LocaleList(locale))
        return base.createConfigurationContext(config)
    }

    /**
     * 언어를 [tag]로 바꾸고 앱을 재시작한다. 이미 같은 언어면 아무것도 안 한다.
     * 재시작은 문제 콘텐츠까지 새 언어로 바꾸기 위한 것(콘텐츠는 프로세스 lazy 캐시 + DB 시딩).
     */
    fun apply(
        context: Context,
        tag: String,
    ) {
        if (currentLang(context) == tag && storedTag(context) == tag) return
        prefs(context).edit().putString(KEY_LANG, tag).apply()
        // 33+에서는 시스템 per-app 언어 설정과도 맞춰 둔다(설정 앱의 언어 선택과 일관).
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            runCatching {
                context
                    .getSystemService(LocaleManager::class.java)
                    ?.applicationLocales = LocaleList.forLanguageTags(tag)
            }
        }
        restart(context)
    }

    /** 런처 액티비티를 새 태스크로 다시 띄우고 현재 프로세스를 종료한다(완전한 콜드 재시작). */
    private fun restart(context: Context) {
        val intent =
            context.packageManager.getLaunchIntentForPackage(context.packageName)?.apply {
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK)
            }
        if (intent != null) {
            context.startActivity(intent)
        }
        Runtime.getRuntime().exit(0)
    }
}
