package com.ddakpul.math.core.designsystem.component

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp

/** 4지선다 보기 하나. 앞에 A·B·C·D 배지를 붙여 아이가 쉽게 구분하도록 한다. */
@Composable
fun ChoiceOption(
    index: Int,
    text: String,
    state: ChoiceState,
    onClick: () -> Unit,
    enabled: Boolean,
    modifier: Modifier = Modifier,
) {
    val colors = MaterialTheme.colorScheme
    val (container, content, border) =
        when (state) {
            ChoiceState.DEFAULT -> {
                Triple(colors.surfaceContainer, colors.onSurface, colors.outlineVariant)
            }

            ChoiceState.SELECTED -> {
                Triple(colors.primaryContainer, colors.onPrimaryContainer, colors.primary)
            }

            ChoiceState.CORRECT -> {
                Triple(colors.secondaryContainer, colors.onSecondaryContainer, colors.secondary)
            }

            ChoiceState.WRONG_SELECTED -> {
                Triple(colors.errorContainer, colors.onErrorContainer, colors.error)
            }

            ChoiceState.DIMMED -> {
                Triple(colors.surfaceContainer, colors.onSurfaceVariant, colors.outlineVariant)
            }
        }

    Card(
        onClick = onClick,
        enabled = enabled,
        modifier = modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = container, contentColor = content),
        border = BorderStroke(2.dp, border),
    ) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(16.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            Surface(
                color = border,
                shape = CircleShape,
                modifier = Modifier.size(32.dp),
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Text(
                        text = ('A' + index).toString(),
                        color = Color.White,
                        fontWeight = FontWeight.Bold,
                        style = MaterialTheme.typography.titleMedium,
                    )
                }
            }
            Text(
                text = text,
                style = MaterialTheme.typography.bodyLarge,
                textAlign = TextAlign.Start,
            )
        }
    }
}
