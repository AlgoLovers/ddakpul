package com.ddakpul.math.core.designsystem.component

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.RoundRect
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.PathEffect
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.drawText
import androidx.compose.ui.text.rememberTextMeasurer
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

// 리포트용 미니 차트 모음. 전부 단일 시리즈라 범례 없이 직접 라벨만 쓰고,
// 그리드·축은 희미하게(outlineVariant), 데이터 마크는 가늘게 그린다.

/**
 * 난이도 [min]~[max] 진행 트랙. 지나온 단계는 옅게, 현재 단계는 진하게, 남은 단계는 비워
 * '어디까지 왔는지'를 한눈에 보여준다(이 앱의 성장 = 난이도 등반, 학년 개념 없음).
 */
@Composable
fun LevelTrack(
    current: Int,
    min: Int,
    max: Int,
    modifier: Modifier = Modifier,
) {
    val primary = MaterialTheme.colorScheme.primary
    val past = primary.copy(alpha = 0.4f)
    val future = MaterialTheme.colorScheme.surfaceVariant
    Row(
        modifier = modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        for (level in min..max) {
            val color =
                when {
                    level < current -> past
                    level == current -> primary
                    else -> future
                }
            Box(
                modifier =
                    Modifier
                        .weight(1f)
                        .height(10.dp)
                        .clip(RoundedCornerShape(5.dp))
                        .background(color),
            )
        }
    }
}

/** 일별 학습량 막대 차트. 값 라벨은 최대값과 강조 칸에만 붙인다(라벨 과다 방지). */
@Composable
fun MiniBarChart(
    entries: List<BarEntry>,
    startLabel: String,
    endLabel: String,
    modifier: Modifier = Modifier,
) {
    val barColor = MaterialTheme.colorScheme.primary
    val mutedBar = barColor.copy(alpha = 0.45f)
    val baseline = MaterialTheme.colorScheme.outlineVariant
    val labelColor = MaterialTheme.colorScheme.onSurfaceVariant
    val textMeasurer = rememberTextMeasurer()
    val labelStyle = TextStyle(fontSize = 10.sp, color = labelColor)

    Column(modifier = modifier.fillMaxWidth(), verticalArrangement = Arrangement.spacedBy(4.dp)) {
        Canvas(modifier = Modifier.fillMaxWidth().height(120.dp)) {
            val max = entries.maxOfOrNull { it.value }?.takeIf { it > 0f } ?: 1f
            val n = entries.size
            if (n == 0) return@Canvas
            val gap = 2.dp.toPx()
            val labelSpace = 14.dp.toPx()
            val chartHeight = size.height - 1.dp.toPx()
            val barWidth = (size.width - gap * (n - 1)) / n
            val maxIndex = entries.indexOfFirst { it.value == entries.maxOf { e -> e.value } }

            // 베이스라인
            drawLine(
                color = baseline,
                start = Offset(0f, chartHeight),
                end = Offset(size.width, chartHeight),
                strokeWidth = 1.dp.toPx(),
            )

            entries.forEachIndexed { index, entry ->
                if (entry.value <= 0f) return@forEachIndexed
                val h = ((entry.value / max) * (chartHeight - labelSpace)).coerceAtLeast(2.dp.toPx())
                val left = index * (barWidth + gap)
                val top = chartHeight - h
                val radius = CornerRadius(4.dp.toPx(), 4.dp.toPx())
                // 데이터 끝(위)만 둥글고 베이스라인 쪽은 각지게.
                val path =
                    Path().apply {
                        addRoundRect(
                            RoundRect(
                                left = left,
                                top = top,
                                right = left + barWidth,
                                bottom = chartHeight,
                                topLeftCornerRadius = radius,
                                topRightCornerRadius = radius,
                            ),
                        )
                    }
                drawPath(path, color = if (entry.emphasized) barColor else mutedBar)

                // 값 라벨은 최대값·강조 칸에만.
                if (index == maxIndex || entry.emphasized) {
                    val text = entry.value.toInt().toString()
                    val measured = textMeasurer.measure(text, labelStyle)
                    drawText(
                        textLayoutResult = measured,
                        topLeft =
                            Offset(
                                x = (left + barWidth / 2 - measured.size.width / 2).coerceIn(0f, size.width - measured.size.width),
                                y = (top - measured.size.height - 2.dp.toPx()).coerceAtLeast(0f),
                            ),
                    )
                }
            }
        }
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            Text(startLabel, style = MaterialTheme.typography.labelSmall, color = labelColor)
            Text(endLabel, style = MaterialTheme.typography.labelSmall, color = labelColor)
        }
    }
}

/**
 * 추이 라인 차트(0~1 비율). [values]는 시간순이며 null은 데이터 없는 칸(선을 잇지 않는다).
 * 마지막 점에만 직접 라벨을 붙인다.
 */
@Composable
fun TrendLineChart(
    values: List<Float?>,
    startLabel: String,
    endLabel: String,
    modifier: Modifier = Modifier,
    lastValueFormatter: (Float) -> String = { "${(it * 100).toInt()}%" },
) {
    val lineColor = MaterialTheme.colorScheme.primary
    val gridColor = MaterialTheme.colorScheme.outlineVariant
    val labelColor = MaterialTheme.colorScheme.onSurfaceVariant
    val textMeasurer = rememberTextMeasurer()
    val labelStyle = TextStyle(fontSize = 10.sp, color = labelColor)

    Column(modifier = modifier.fillMaxWidth(), verticalArrangement = Arrangement.spacedBy(4.dp)) {
        Canvas(modifier = Modifier.fillMaxWidth().height(120.dp)) {
            val n = values.size
            if (n == 0) return@Canvas
            val pad = 6.dp.toPx()
            val w = size.width - pad * 2
            val h = size.height - pad * 2

            fun x(i: Int) = pad + if (n == 1) w / 2 else w * i / (n - 1)

            fun y(v: Float) = pad + h * (1f - v.coerceIn(0f, 1f))

            // 희미한 그리드: 0% / 50% / 100%
            listOf(0f, 0.5f, 1f).forEach { level ->
                drawLine(
                    color = gridColor,
                    start = Offset(pad, y(level)),
                    end = Offset(size.width - pad, y(level)),
                    strokeWidth = 1.dp.toPx(),
                    pathEffect = if (level == 0.5f) PathEffect.dashPathEffect(floatArrayOf(8f, 8f)) else null,
                )
            }

            // 데이터 있는 이웃끼리만 선으로 잇는다.
            var prev: Pair<Int, Float>? = null
            values.forEachIndexed { i, v ->
                if (v == null) return@forEachIndexed
                prev?.let { (pi, pv) ->
                    drawLine(
                        color = lineColor,
                        start = Offset(x(pi), y(pv)),
                        end = Offset(x(i), y(v)),
                        strokeWidth = 2.dp.toPx(),
                        cap = StrokeCap.Round,
                    )
                }
                drawCircle(color = lineColor, radius = 4.dp.toPx() / 2, center = Offset(x(i), y(v)))
                prev = i to v
            }

            // 마지막 점 직접 라벨
            prev?.let { (i, v) ->
                val text = lastValueFormatter(v)
                val measured = textMeasurer.measure(text, labelStyle)
                drawText(
                    textLayoutResult = measured,
                    topLeft =
                        Offset(
                            x = (x(i) - measured.size.width - 4.dp.toPx()).coerceAtLeast(0f),
                            y = (y(v) - measured.size.height - 4.dp.toPx()).coerceAtLeast(0f),
                        ),
                )
            }
        }
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            Text(startLabel, style = MaterialTheme.typography.labelSmall, color = labelColor)
            Text(endLabel, style = MaterialTheme.typography.labelSmall, color = labelColor)
        }
    }
}

/** 난이도 성장 곡선 — 시도 순서에 따른 난이도(1~7)를 계단선으로 그린다. */
@Composable
fun StepLineChart(
    values: List<Int>,
    minValue: Int,
    maxValue: Int,
    modifier: Modifier = Modifier,
) {
    val lineColor = MaterialTheme.colorScheme.primary
    val gridColor = MaterialTheme.colorScheme.outlineVariant
    val labelColor = MaterialTheme.colorScheme.onSurfaceVariant
    val textMeasurer = rememberTextMeasurer()
    val labelStyle = TextStyle(fontSize = 10.sp, color = labelColor)

    Canvas(modifier = modifier.fillMaxWidth().height(110.dp)) {
        if (values.isEmpty() || maxValue <= minValue) return@Canvas
        val pad = 6.dp.toPx()
        val leftPad = 18.dp.toPx()
        val w = size.width - leftPad - pad
        val h = size.height - pad * 2
        val n = values.size

        fun x(i: Int) = leftPad + if (n == 1) w / 2 else w * i / (n - 1)

        fun y(v: Int) = pad + h * (1f - (v - minValue).toFloat() / (maxValue - minValue))

        // 레벨 그리드 + 좌측 라벨(위·아래만)
        for (level in minValue..maxValue) {
            drawLine(
                color = gridColor,
                start = Offset(leftPad, y(level)),
                end = Offset(size.width - pad, y(level)),
                strokeWidth = 1.dp.toPx(),
            )
            if (level == minValue || level == maxValue) {
                val measured = textMeasurer.measure(level.toString(), labelStyle)
                drawText(
                    textLayoutResult = measured,
                    topLeft = Offset(0f, y(level) - measured.size.height / 2),
                )
            }
        }

        // 계단선
        val path =
            Path().apply {
                values.forEachIndexed { i, v ->
                    if (i == 0) {
                        moveTo(x(0), y(v))
                    } else {
                        lineTo(x(i), y(values[i - 1]))
                        lineTo(x(i), y(v))
                    }
                }
            }
        drawPath(path, color = lineColor, style = Stroke(width = 2.dp.toPx(), cap = StrokeCap.Round))
        values.lastIndex.let { last ->
            drawCircle(color = lineColor, radius = 3.dp.toPx(), center = Offset(x(last), y(values[last])))
        }
    }
}
