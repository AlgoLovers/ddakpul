package com.ddakpul.math.core.designsystem.theme

import androidx.compose.material3.Typography
import androidx.compose.ui.text.ExperimentalTextApi
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.Font
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontVariation
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp
import com.ddakpul.math.R

// Pretendard(OFL) — 한글·라틴 모두 완성도 높은 본문 서체. 앱 실제 사용 글자만 서브셋해 내장(≈0.4MB,
// tools/fonts/subset.py). 가변 폰트라 한 파일로 여러 두께를 낸다(빠진 글자는 시스템 폰트로 자연 대체).
@OptIn(ExperimentalTextApi::class)
private fun pretendard(weight: Int) =
    Font(
        resId = R.font.pretendard,
        weight = FontWeight(weight),
        variationSettings = FontVariation.Settings(FontVariation.weight(weight)),
    )

val Pretendard =
    FontFamily(
        pretendard(400),
        pretendard(500),
        pretendard(600),
        pretendard(700),
    )

// 아이가 읽기 편하도록 본문·문제 문장은 기본보다 살짝 크게 잡는다. 나머지 스타일은 M3 기본 크기에
// 서체만 Pretendard로 바꿔 전체를 일관되게 한다.
private val base = Typography()

val Typography =
    Typography(
        displayLarge = base.displayLarge.copy(fontFamily = Pretendard),
        displayMedium = base.displayMedium.copy(fontFamily = Pretendard),
        displaySmall = base.displaySmall.copy(fontFamily = Pretendard),
        headlineLarge = base.headlineLarge.copy(fontFamily = Pretendard),
        headlineMedium =
            TextStyle(
                fontFamily = Pretendard,
                fontWeight = FontWeight.Bold,
                fontSize = 28.sp,
                lineHeight = 36.sp,
            ),
        headlineSmall = base.headlineSmall.copy(fontFamily = Pretendard),
        titleLarge =
            TextStyle(
                fontFamily = Pretendard,
                fontWeight = FontWeight.Bold,
                fontSize = 22.sp,
                lineHeight = 28.sp,
            ),
        titleMedium = base.titleMedium.copy(fontFamily = Pretendard),
        titleSmall = base.titleSmall.copy(fontFamily = Pretendard),
        bodyLarge =
            TextStyle(
                fontFamily = Pretendard,
                fontWeight = FontWeight.Normal,
                fontSize = 18.sp,
                lineHeight = 26.sp,
                letterSpacing = 0.3.sp,
            ),
        bodyMedium =
            TextStyle(
                fontFamily = Pretendard,
                fontWeight = FontWeight.Normal,
                fontSize = 15.sp,
                lineHeight = 22.sp,
                letterSpacing = 0.2.sp,
            ),
        bodySmall = base.bodySmall.copy(fontFamily = Pretendard),
        labelLarge = base.labelLarge.copy(fontFamily = Pretendard),
        labelMedium = base.labelMedium.copy(fontFamily = Pretendard),
        labelSmall = base.labelSmall.copy(fontFamily = Pretendard),
    )
