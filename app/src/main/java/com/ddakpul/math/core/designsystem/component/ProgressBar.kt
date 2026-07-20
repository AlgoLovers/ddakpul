package com.ddakpul.math.core.designsystem.component

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp

/**
 * 트랙 위에 비율만큼 채우는 둥근 가로 막대(리포트의 평균시간·영역 성취 등 공용).
 * 모서리는 알약 모양이 되게 높이의 절반으로 둔다. 폭은 호출부가 [modifier]로 정한다
 * (Row 안에서는 `Modifier.weight(1f)`, 전체폭이면 `Modifier.fillMaxWidth()`).
 */
@Composable
fun ProgressBar(
    fraction: Float,
    color: Color,
    trackColor: Color,
    modifier: Modifier = Modifier,
    height: Dp = 12.dp,
) {
    val shape = RoundedCornerShape(height / 2)
    Box(modifier = modifier.height(height).clip(shape).background(trackColor)) {
        Box(
            Modifier
                .fillMaxWidth(fraction.coerceIn(0f, 1f))
                .height(height)
                .clip(shape)
                .background(color),
        )
    }
}
