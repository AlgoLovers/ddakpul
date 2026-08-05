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
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.selected
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.semantics.stateDescription
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.ddakpul.math.R

/** 채점 결과를 색이 아니라 말로도 전달한다 — 스크린리더·색각 이상 사용자를 위해. */
@Composable
private fun ChoiceState.stateLabel(): String? =
    when (this) {
        ChoiceState.CORRECT -> stringResource(R.string.choice_state_correct)
        ChoiceState.WRONG_SELECTED -> stringResource(R.string.choice_state_wrong)
        ChoiceState.SELECTED -> stringResource(R.string.choice_state_selected)
        ChoiceState.DEFAULT, ChoiceState.DIMMED -> null
    }

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

    // 채점 뒤 어느 것이 정답인지 색으로만 알려주면 스크린리더·색각 이상 사용자는 알 수 없다.
    val stateLabel = state.stateLabel()
    Card(
        onClick = onClick,
        enabled = enabled,
        modifier =
            modifier
                .fillMaxWidth()
                .semantics {
                    selected = state == ChoiceState.SELECTED
                    stateLabel?.let { stateDescription = it }
                },
        colors = CardDefaults.cardColors(containerColor = container, contentColor = content),
        border = BorderStroke(2.dp, border),
    ) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(16.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            // 배지 글자색은 배지 배경과 짝으로 — 기본 상태의 옅은 회색 원에 흰 글자는 대비 미달.
            // 배지 원 위 글자는 반드시 그 배경의 짝 색으로 — 흰 글자는 라이트 2.8:1,
            // 다크 1.6:1까지 떨어져 A·B·C·D가 사실상 안 보인다(DESIGN.md 하드룰 2·5).
            val badgeContent =
                when (state) {
                    ChoiceState.DEFAULT, ChoiceState.DIMMED -> colors.onSurfaceVariant
                    ChoiceState.SELECTED -> colors.onPrimary
                    ChoiceState.CORRECT -> colors.onSecondary
                    ChoiceState.WRONG_SELECTED -> colors.onError
                }
            Surface(
                color = border,
                shape = CircleShape,
                modifier = Modifier.size(32.dp),
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Text(
                        text = ('A' + index).toString(),
                        color = badgeContent,
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
