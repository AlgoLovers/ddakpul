package com.ddakpul.math.core.designsystem.component

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp

/**
 * 목표 칸 점 진행 — 총 [total]칸 중 [solved]칸을 채운다(홈 목표 카드·풀이 진행 공용).
 * 근접 목표는 "셀 수 있어야" 힘이 생긴다 — 연속 막대 대신 낱개 칸으로 보여주는 이유.
 * [highlightNext]가 true면 다음 칸(지금 풀고 있는 문제)을 primary로 강조한다.
 */
@Composable
fun ProgressDots(
    solved: Int,
    total: Int,
    modifier: Modifier = Modifier,
    highlightNext: Boolean = false,
    height: Dp = 8.dp,
) {
    val colors = MaterialTheme.colorScheme
    Row(modifier = modifier, horizontalArrangement = Arrangement.spacedBy(5.dp)) {
        repeat(total) { index ->
            val color =
                when {
                    index < solved -> colors.secondary

                    highlightNext && index == solved -> colors.primary

                    // outlineVariant는 배경 대비 1.2:1이라 '아직 안 푼 칸'이 안 보인다.
                    else -> colors.outline
                }
            Box(
                modifier =
                    Modifier
                        .weight(1f)
                        .height(height)
                        .clip(RoundedCornerShape(height / 2))
                        .background(color),
            )
        }
    }
}
