package com.ddakpul.math.core.designsystem.component

import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.ddakpul.math.R

/** 숙달 단계 — 점수화 대신 라벨로 보여준다(색만으로 구분하지 않는다). */
enum class MasteryStage { NOT_ATTEMPTED, WEAK, PRACTICING, MASTERED }

private const val MASTERED_ACCURACY = 0.8f
private const val WEAK_ACCURACY = 0.6f
private const val MIN_SOLVED_FOR_MASTERY = 3

/** [solved]가 0이면 항상 시도 전. 그 외엔 정답률·풀이 수 기준으로 3단계 판정. */
fun masteryStageOf(
    solved: Int,
    accuracy: Float,
): MasteryStage =
    when {
        solved == 0 -> MasteryStage.NOT_ATTEMPTED
        accuracy >= MASTERED_ACCURACY && solved >= MIN_SOLVED_FOR_MASTERY -> MasteryStage.MASTERED
        accuracy < WEAK_ACCURACY -> MasteryStage.WEAK
        else -> MasteryStage.PRACTICING
    }

internal data class MasteryColors(
    val container: Color,
    val content: Color,
)

@Composable
internal fun MasteryStage.colors(): MasteryColors {
    val colors = MaterialTheme.colorScheme
    return when (this) {
        MasteryStage.MASTERED -> MasteryColors(colors.secondaryContainer, colors.onSecondaryContainer)
        MasteryStage.PRACTICING -> MasteryColors(colors.tertiaryContainer, colors.onTertiaryContainer)
        MasteryStage.WEAK -> MasteryColors(colors.errorContainer, colors.onErrorContainer)
        MasteryStage.NOT_ATTEMPTED -> MasteryColors(colors.surfaceVariant, colors.onSurfaceVariant)
    }
}

private fun MasteryStage.labelRes(): Int =
    when (this) {
        MasteryStage.MASTERED -> R.string.mastery_mastered
        MasteryStage.PRACTICING -> R.string.mastery_practicing
        MasteryStage.WEAK -> R.string.mastery_weak
        MasteryStage.NOT_ATTEMPTED -> R.string.mastery_not_attempted
    }

/** 숙달 단계를 색+텍스트로 함께 보여주는 칩. */
@Composable
fun MasteryChip(
    stage: MasteryStage,
    modifier: Modifier = Modifier,
) {
    val (container, content) = stage.colors()
    Surface(modifier = modifier, color = container, contentColor = content, shape = MaterialTheme.shapes.small) {
        Text(
            text = stringResource(stage.labelRes()),
            style = MaterialTheme.typography.labelMedium,
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 3.dp),
        )
    }
}
