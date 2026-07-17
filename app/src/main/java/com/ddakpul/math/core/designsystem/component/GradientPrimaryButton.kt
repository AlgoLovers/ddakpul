package com.ddakpul.math.core.designsystem.component

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.RowScope
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.LocalContentColor
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.lerp
import androidx.compose.ui.unit.dp

/**
 * 주요 행동(CTA) 버튼 — 브랜드 색의 세로 그라데이션 + 컬러 소프트 섀도우로 입체감을 준다.
 * 색을 테마의 primary에서 파생(위=살짝 밝게, 아래=살짝 어둡게)하므로 라이트/다크 모두 자연스럽다.
 * 의존성 없이 순수 Compose. 내용(아이콘·텍스트)은 onPrimary 색을 자동 상속한다.
 */
@Composable
fun GradientPrimaryButton(
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    content: @Composable RowScope.() -> Unit,
) {
    val colors = MaterialTheme.colorScheme
    val shape = RoundedCornerShape(28.dp)
    val top = lerp(colors.primary, Color.White, HIGHLIGHT_FRACTION)
    val bottom = lerp(colors.primary, Color.Black, SHADE_FRACTION)
    Row(
        modifier =
            modifier
                .shadow(elevation = 10.dp, shape = shape, spotColor = colors.primary, ambientColor = colors.primary)
                .clip(shape)
                .background(Brush.verticalGradient(listOf(top, bottom)))
                .clickable(onClick = onClick)
                .padding(vertical = 16.dp, horizontal = 24.dp),
        horizontalArrangement = Arrangement.Center,
        verticalAlignment = Alignment.CenterVertically,
    ) {
        CompositionLocalProvider(LocalContentColor provides colors.onPrimary, content = { content() })
    }
}

private const val HIGHLIGHT_FRACTION = 0.16f
private const val SHADE_FRACTION = 0.14f
