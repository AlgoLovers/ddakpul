package com.ddakpul.math.core.designsystem.component

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import kotlin.math.roundToInt

/**
 * [rowLabels] × [columnLabels] 히트맵. [cells]는 row-major 순서
 * (row0col0, row0col1, ..., row1col0, ...)로 rowLabels.size * columnLabels.size개여야 한다.
 */
@Composable
fun MasteryMatrix(
    rowLabels: List<String>,
    columnLabels: List<String>,
    cells: List<MatrixEntry>,
    modifier: Modifier = Modifier,
) {
    require(cells.size == rowLabels.size * columnLabels.size) {
        "cells.size(${cells.size})는 rowLabels(${rowLabels.size}) * columnLabels(${columnLabels.size})와 같아야 한다"
    }
    val rowLabelWidth = 88.dp
    val labelColor = MaterialTheme.colorScheme.onSurfaceVariant

    Column(modifier = modifier.fillMaxWidth(), verticalArrangement = Arrangement.spacedBy(4.dp)) {
        Row(modifier = Modifier.fillMaxWidth()) {
            Box(modifier = Modifier.width(rowLabelWidth))
            columnLabels.forEach { label ->
                Text(
                    text = label,
                    style = MaterialTheme.typography.labelSmall,
                    color = labelColor,
                    textAlign = TextAlign.Center,
                    modifier = Modifier.weight(1f),
                )
            }
        }
        val rows = cells.chunked(columnLabels.size)
        rowLabels.forEachIndexed { rowIndex, rowLabel ->
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(
                    text = rowLabel,
                    style = MaterialTheme.typography.labelSmall,
                    color = labelColor,
                    modifier = Modifier.width(rowLabelWidth),
                )
                rows[rowIndex].forEach { entry ->
                    MasteryCell(entry = entry, modifier = Modifier.weight(1f).padding(2.dp))
                }
            }
        }
    }
}

@Composable
private fun MasteryCell(
    entry: MatrixEntry,
    modifier: Modifier = Modifier,
) {
    val stage = masteryStageOf(entry.solved, entry.accuracy ?: 0f)
    val (container, content) = stage.colors()
    val border =
        if (entry.emphasized) {
            BorderStroke(2.dp, MaterialTheme.colorScheme.primary)
        } else {
            null
        }
    Surface(
        modifier = modifier.aspectRatio(1f),
        color = container,
        contentColor = content,
        border = border,
        shape = MaterialTheme.shapes.small,
    ) {
        Box(contentAlignment = Alignment.Center, modifier = Modifier.fillMaxSize()) {
            Text(
                text = entry.accuracy?.let { "${(it * 100).roundToInt()}%" } ?: "-",
                style = MaterialTheme.typography.labelSmall,
            )
        }
    }
}
