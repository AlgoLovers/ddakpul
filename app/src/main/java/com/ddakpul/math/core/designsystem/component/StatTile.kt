package com.ddakpul.math.core.designsystem.component

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp

/**
 * 라벨 + 큰 값 한 쌍을 보여주는 통계 타일(홈·리포트 공용).
 * [icon]은 값 위 이모지, [caption]은 라벨 아래 보조 수치(둘 다 선택).
 * [iconTint]를 주면 아이콘을 파스텔 원형 배지 안에 담아 생기를 준다.
 * 배지 없이(=iconTint null) 이모지만 두면 목업의 담백한 카드 스타일이 된다.
 * [containerColor]로 카드 배경을 조절한다(기본=흰 카드, 옅은 회색 카드도 지정 가능).
 */
@Composable
fun StatTile(
    label: String,
    value: String,
    modifier: Modifier = Modifier,
    icon: String? = null,
    caption: String? = null,
    iconTint: Color? = null,
    containerColor: Color = MaterialTheme.colorScheme.surfaceContainer,
) {
    Card(
        modifier = modifier,
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(containerColor = containerColor),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp),
    ) {
        Column(
            modifier = Modifier.fillMaxWidth().padding(vertical = 16.dp, horizontal = 12.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(6.dp),
        ) {
            if (icon != null) {
                if (iconTint != null) {
                    Box(
                        modifier =
                            Modifier
                                .size(52.dp)
                                .background(iconTint.copy(alpha = 0.16f), CircleShape),
                        contentAlignment = Alignment.Center,
                    ) {
                        Text(text = icon, style = MaterialTheme.typography.titleMedium)
                    }
                } else {
                    Text(text = icon, style = MaterialTheme.typography.headlineSmall)
                }
            }
            Text(
                text = value,
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.primary,
                maxLines = 1,
                softWrap = false,
            )
            Text(
                text = label,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            if (caption != null) {
                Text(
                    text = caption,
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        }
    }
}
