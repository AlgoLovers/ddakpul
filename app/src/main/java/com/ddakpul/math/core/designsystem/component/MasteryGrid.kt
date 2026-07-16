package com.ddakpul.math.core.designsystem.component

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
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
 *
 * 난이도 열이 천장 상향으로 계속 늘 수 있어(1~9, 그 이상), 셀은 고정 크기로 두고 가로 스크롤한다.
 * 영역 라벨 열은 왼쪽에 고정(pin)해 스크롤해도 어느 영역인지 놓치지 않는다.
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
    val cellSize = 40.dp
    val labelColor = MaterialTheme.colorScheme.onSurfaceVariant
    val rows = cells.chunked(columnLabels.size)

    Row(modifier = modifier) {
        // 왼쪽 고정 영역 라벨 열 — 헤더 높이(라벨행)만큼 띄우고 각 행을 셀 높이에 맞춘다.
        Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
            Box(modifier = Modifier.height(cellSize).width(rowLabelWidth))
            rowLabels.forEach { rowLabel ->
                Box(modifier = Modifier.height(cellSize).width(rowLabelWidth), contentAlignment = Alignment.CenterStart) {
                    Text(text = rowLabel, style = MaterialTheme.typography.labelSmall, color = labelColor)
                }
            }
        }
        // 오른쪽 스크롤되는 난이도 열들.
        Column(
            modifier = Modifier.horizontalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(4.dp),
        ) {
            Row {
                columnLabels.forEach { label ->
                    Box(modifier = Modifier.size(cellSize), contentAlignment = Alignment.Center) {
                        Text(
                            text = label,
                            style = MaterialTheme.typography.labelSmall,
                            color = labelColor,
                            textAlign = TextAlign.Center,
                        )
                    }
                }
            }
            rowLabels.indices.forEach { rowIndex ->
                Row {
                    rows[rowIndex].forEach { entry ->
                        MasteryCell(entry = entry, modifier = Modifier.size(cellSize).padding(2.dp))
                    }
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
        modifier = modifier,
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
