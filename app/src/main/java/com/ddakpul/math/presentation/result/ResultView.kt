package com.ddakpul.math.presentation.result

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Lightbulb
import androidx.compose.material.icons.filled.WarningAmber
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.ddakpul.math.R
import com.ddakpul.math.domain.model.GradingResult

/**
 * 채점 결과 화면. 정답/오답 배너, 내가 고른 답과 정답, (있으면) 오개념 피드백과 해설을 보여준다.
 * [showExplanation]이 true면(정체 감지) 기초부터 다시 하자는 안내를 강조한다.
 */
@Composable
fun ResultView(
    result: GradingResult,
    showExplanation: Boolean,
    onNext: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val colors = MaterialTheme.colorScheme
    Column(
        modifier = modifier.fillMaxWidth().verticalScroll(rememberScrollState()).padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        // 정답/오답 배너
        Card(
            colors =
                CardDefaults.cardColors(
                    containerColor = if (result.isCorrect) colors.secondaryContainer else colors.errorContainer,
                    contentColor = if (result.isCorrect) colors.onSecondaryContainer else colors.onErrorContainer,
                ),
            modifier = Modifier.fillMaxWidth(),
        ) {
            Row(
                modifier = Modifier.fillMaxWidth().padding(20.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                Icon(
                    imageVector = if (result.isCorrect) Icons.Filled.CheckCircle else Icons.Filled.WarningAmber,
                    contentDescription = null,
                )
                Text(
                    text = stringResource(if (result.isCorrect) R.string.result_correct else R.string.result_wrong),
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold,
                )
            }
        }

        val choices = result.problem.choices
        Text(
            text = stringResource(R.string.result_correct_answer, choices[result.correctIndex]),
            style = MaterialTheme.typography.bodyLarge,
            fontWeight = FontWeight.Bold,
        )
        if (!result.isCorrect) {
            Text(
                text = stringResource(R.string.result_your_answer, choices[result.selectedIndex]),
                style = MaterialTheme.typography.bodyMedium,
                color = colors.onSurfaceVariant,
            )
        }

        // 오개념 피드백(고른 오답에 맞는 설명이 있을 때)
        result.mistake?.let { mistake ->
            FeedbackCard(
                icon = Icons.Filled.WarningAmber,
                container = colors.tertiaryContainer,
                content = colors.onTertiaryContainer,
                label = stringResource(R.string.result_mistake_label),
                body = mistake.misconception,
            )
        }

        // 해설(대표문제에 있을 때)
        result.explanation?.let { explanation ->
            FeedbackCard(
                icon = Icons.Filled.Lightbulb,
                container = colors.surfaceContainerHigh,
                content = colors.onSurface,
                label = stringResource(R.string.result_explanation_label),
                body = explanation,
            )
        }

        if (showExplanation) {
            Text(
                text = stringResource(R.string.result_remediation_hint),
                style = MaterialTheme.typography.bodyMedium,
                color = colors.primary,
                fontWeight = FontWeight.Bold,
            )
        }

        Button(
            onClick = onNext,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(
                text = stringResource(R.string.result_next),
                style = MaterialTheme.typography.titleMedium,
                modifier = Modifier.padding(vertical = 6.dp),
            )
        }
    }
}

@Composable
private fun FeedbackCard(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    container: androidx.compose.ui.graphics.Color,
    content: androidx.compose.ui.graphics.Color,
    label: String,
    body: String,
) {
    Card(
        colors = CardDefaults.cardColors(containerColor = container, contentColor = content),
        modifier = Modifier.fillMaxWidth(),
    ) {
        Column(
            modifier = Modifier.fillMaxWidth().padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                Icon(imageVector = icon, contentDescription = null)
                Text(text = label, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
            }
            Text(text = body, style = MaterialTheme.typography.bodyMedium)
        }
    }
}
