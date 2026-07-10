package com.ddakpul.math.core.designsystem.component

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.drawText
import androidx.compose.ui.text.rememberTextMeasurer
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.ddakpul.math.domain.model.FigureType
import com.ddakpul.math.domain.model.ProblemFigure
import kotlin.math.cos
import kotlin.math.min
import kotlin.math.sin

/** 문제 도형 렌더러 — 지시서([ProblemFigure])를 받아 Canvas로 그린다. */
@Composable
fun ProblemFigureView(
    figure: ProblemFigure,
    modifier: Modifier = Modifier,
) {
    val ink = MaterialTheme.colorScheme.onSurface
    val accent = MaterialTheme.colorScheme.primary
    val textMeasurer = rememberTextMeasurer()
    val labelStyle = TextStyle(fontSize = 12.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)

    Canvas(modifier = modifier.fillMaxWidth().height(170.dp)) {
        val side = min(size.width, size.height) * 0.85f
        val left = (size.width - side) / 2f
        val top = (size.height - side) / 2f
        when (figure.type) {
            FigureType.CLOCK -> {
                drawClock(figure, ink, accent, left, top, side)
            }

            FigureType.DOT_BORDER -> {
                drawDotBorder(figure, ink, left, top, side)
            }

            FigureType.GRID -> {
                drawGrid(figure, ink, accent, left, top, side)
            }

            FigureType.L_SHAPE -> {
                drawLShape(figure, ink, left, top, side) { text, x, y ->
                    val measured = textMeasurer.measure(text, labelStyle)
                    drawText(measured, topLeft = Offset(x - measured.size.width / 2f, y - measured.size.height / 2f))
                }
            }
        }
    }
}

private fun DrawScope.drawClock(
    figure: ProblemFigure,
    ink: Color,
    accent: Color,
    left: Float,
    top: Float,
    side: Float,
) {
    val hour = figure.params["hour"] ?: 12
    val minute = figure.params["minute"] ?: 0
    val center = Offset(left + side / 2, top + side / 2)
    val radius = side / 2
    drawCircle(color = ink, radius = radius, center = center, style = Stroke(width = 3f))
    // 12개 눈금 (숫자 없는 시계 — 거울 문제에서도 공정하게)
    for (i in 0 until 12) {
        val angle = Math.toRadians(i * 30.0 - 90).toFloat()
        val outer = center + Offset(cos(angle) * radius * 0.95f, sin(angle) * radius * 0.95f)
        val inner = center + Offset(cos(angle) * radius * 0.82f, sin(angle) * radius * 0.82f)
        drawLine(ink, inner, outer, strokeWidth = if (i % 3 == 0) 4f else 2f)
    }
    val hourAngle = Math.toRadians(((hour % 12) * 30 + minute * 0.5) - 90).toFloat()
    val minuteAngle = Math.toRadians(minute * 6.0 - 90).toFloat()
    drawLine(accent, center, center + Offset(cos(hourAngle) * radius * 0.5f, sin(hourAngle) * radius * 0.5f), strokeWidth = 7f)
    drawLine(ink, center, center + Offset(cos(minuteAngle) * radius * 0.75f, sin(minuteAngle) * radius * 0.75f), strokeWidth = 4f)
    drawCircle(ink, radius = 5f, center = center)
}

private fun DrawScope.drawDotBorder(
    figure: ProblemFigure,
    ink: Color,
    left: Float,
    top: Float,
    side: Float,
) {
    val n = (figure.params["side"] ?: 6).coerceIn(3, 20)
    val step = side / (n - 1)
    val r = (step * 0.28f).coerceAtMost(9f)
    for (row in 0 until n) {
        for (col in 0 until n) {
            val isBorder = row == 0 || row == n - 1 || col == 0 || col == n - 1
            if (isBorder) {
                drawCircle(ink, radius = r, center = Offset(left + col * step, top + row * step))
            }
        }
    }
}

private fun DrawScope.drawGrid(
    figure: ProblemFigure,
    ink: Color,
    accent: Color,
    left: Float,
    top: Float,
    side: Float,
) {
    val w = (figure.params["w"] ?: 3).coerceIn(1, 8)
    val h = (figure.params["h"] ?: 3).coerceIn(1, 8)
    val cell = min(side / w, side / h)
    val gridLeft = left + (side - cell * w) / 2f
    val gridTop = top + (side - cell * h) / 2f
    for (i in 0..w) {
        drawLine(ink, Offset(gridLeft + i * cell, gridTop), Offset(gridLeft + i * cell, gridTop + h * cell), strokeWidth = 3f)
    }
    for (j in 0..h) {
        drawLine(ink, Offset(gridLeft, gridTop + j * cell), Offset(gridLeft + w * cell, gridTop + j * cell), strokeWidth = 3f)
    }
    if ((figure.params["mark"] ?: 0) == 1) {
        // 출발(왼쪽 아래)·도착(오른쪽 위)
        drawCircle(accent, radius = 9f, center = Offset(gridLeft, gridTop + h * cell))
        drawCircle(accent, radius = 9f, center = Offset(gridLeft + w * cell, gridTop), style = Stroke(width = 5f))
    }
}

private fun DrawScope.drawLShape(
    figure: ProblemFigure,
    ink: Color,
    left: Float,
    top: Float,
    side: Float,
    label: DrawScope.(String, Float, Float) -> Unit,
) {
    val w = (figure.params["w"] ?: 10).toFloat()
    val cutW = (figure.params["cutW"] ?: 4).toFloat()
    val cutH = (figure.params["cutH"] ?: 4).toFloat()
    val scale = side / w
    // 오른쪽 위 모퉁이가 잘린 L자
    val path =
        Path().apply {
            moveTo(left, top)
            lineTo(left + (w - cutW) * scale, top)
            lineTo(left + (w - cutW) * scale, top + cutH * scale)
            lineTo(left + w * scale, top + cutH * scale)
            lineTo(left + w * scale, top + w * scale)
            lineTo(left, top + w * scale)
            close()
        }
    drawPath(path, color = ink, style = Stroke(width = 4f))
    label("${w.toInt()}cm", left + w * scale / 2f, top + w * scale + 16f)
    label("${cutW.toInt()}cm", left + (w - cutW / 2f) * scale, top + cutH * scale - 14f)
    label("${cutH.toInt()}cm", left + (w - cutW) * scale - 22f, top + cutH * scale / 2f)
}
