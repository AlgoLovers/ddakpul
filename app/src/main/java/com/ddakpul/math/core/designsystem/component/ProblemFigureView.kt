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
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.res.stringArrayResource
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.drawText
import androidx.compose.ui.text.rememberTextMeasurer
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.ddakpul.math.R
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
    // 쌓기나무 세 면(윗면·오른면·왼면)을 밝기 차로 입체감 있게.
    val cubeFaces =
        listOf(
            MaterialTheme.colorScheme.surfaceContainerHighest,
            MaterialTheme.colorScheme.surfaceContainerHigh,
            MaterialTheme.colorScheme.surfaceContainer,
        )
    val textMeasurer = rememberTextMeasurer()
    val labelStyle = TextStyle(fontSize = 12.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
    // 막대그래프 범주 라벨은 언어 따라 바뀐다(한국어 가·나·다 / 영어 A·B·C) — 문제 본문과 일치시키려.
    val barLabels = stringArrayResource(R.array.bar_chart_labels)

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

            FigureType.POLYGON -> {
                drawPolygon(figure, ink, accent, left, top, side)
            }

            FigureType.CUBE_STACK -> {
                drawCubeStack(figure, ink, cubeFaces, left, top, side)
            }

            FigureType.GRID_POLYGON -> {
                drawGridPolygon(figure, ink, accent, left, top, side)
            }

            FigureType.TRIANGLE_FAN -> {
                drawTriangleFan(figure, ink, accent, left, top, side)
            }

            FigureType.CUBE_NET -> {
                drawCubeNet(figure, ink, accent, left, top, side)
            }

            FigureType.MATCHSTICK -> {
                drawMatchstick(figure, ink, left, top, side)
            }

            FigureType.BAR_CHART -> {
                drawBarChart(figure, ink, accent, left, top, side, barLabels) { text, x, y ->
                    val measured = textMeasurer.measure(text, labelStyle)
                    drawText(measured, topLeft = Offset(x - measured.size.width / 2f, y - measured.size.height / 2f))
                }
            }
        }
    }
}

/** 막대그래프 — heights의 값들을 막대로 그리고 각 막대 위에 값, 아래에 범주(가·나·다… / A·B·C…)를 쓴다. */
private fun DrawScope.drawBarChart(
    figure: ProblemFigure,
    ink: Color,
    accent: Color,
    left: Float,
    top: Float,
    side: Float,
    barLabels: Array<String>,
    label: DrawScope.(String, Float, Float) -> Unit,
) {
    val values = figure.heights
    if (values.isEmpty()) return
    val n = values.size
    val maxV = (values.maxOrNull() ?: 1).coerceAtLeast(1)
    val highlight = figure.params["highlight"] ?: -1
    val baseY = top + side * 0.86f
    val chartH = side * 0.66f
    val slot = side / n
    val barW = slot * 0.54f
    drawLine(ink, Offset(left, baseY), Offset(left + side, baseY), strokeWidth = 3f)
    for (i in 0 until n) {
        val cx = left + slot * (i + 0.5f)
        val barH = chartH * values[i] / maxV
        drawRect(
            color = if (i == highlight) ink else accent,
            topLeft = Offset(cx - barW / 2f, baseY - barH),
            size = Size(barW, barH),
        )
        label(values[i].toString(), cx, baseY - barH - 12f)
        label(barLabels.getOrElse(i) { "${i + 1}" }, cx, baseY + 16f)
    }
}

/** 성냥개비로 한 줄로 이어 붙인 정사각형(기본) 또는 정삼각형(tri=1, 위아래 번갈아). */
private fun DrawScope.drawMatchstick(
    figure: ProblemFigure,
    ink: Color,
    left: Float,
    top: Float,
    side: Float,
) {
    val n = (figure.params["n"] ?: 3).coerceIn(1, 8)
    val isTri = (figure.params["tri"] ?: 0) == 1
    val stroke = 7f

    fun stick(
        a: Offset,
        b: Offset,
    ) = drawLine(ink, a, b, strokeWidth = stroke, cap = StrokeCap.Round)
    if (!isTri) {
        val s = min(side / n, side * 0.5f)
        val gLeft = left + (side - s * n) / 2f
        val gTop = top + (side - s) / 2f
        stick(Offset(gLeft, gTop), Offset(gLeft + s * n, gTop))
        stick(Offset(gLeft, gTop + s), Offset(gLeft + s * n, gTop + s))
        for (i in 0..n) stick(Offset(gLeft + i * s, gTop), Offset(gLeft + i * s, gTop + s))
    } else {
        val s = min(side * 2f / (n + 1), side * 0.5f)
        val hgt = s * 0.87f
        val totalW = s * (n + 1) / 2f
        val gLeft = left + (side - totalW) / 2f
        val baseY = top + (side + hgt) / 2f
        val topY = baseY - hgt

        fun px(k: Int) = gLeft + k * (s / 2f)

        fun py(k: Int) = if (k % 2 == 0) baseY else topY
        for (i in 0 until n) {
            val a = Offset(px(i), py(i))
            val b = Offset(px(i + 1), py(i + 1))
            val c = Offset(px(i + 2), py(i + 2))
            stick(a, b)
            stick(b, c)
            stick(c, a)
        }
    }
}

/** 정육면체(주사위) 전개도 — 6개 면을 격자에 그리고 눈을 찍는다. 색칠 면(query)은 강조. */
private fun DrawScope.drawCubeNet(
    figure: ProblemFigure,
    ink: Color,
    accent: Color,
    left: Float,
    top: Float,
    side: Float,
) {
    val cols = (figure.params["cols"] ?: 4).coerceIn(1, 12)
    val rows = (figure.params["rows"] ?: 4).coerceIn(1, 12)
    val query = figure.params["query"] ?: -1
    val hs = figure.heights
    if (hs.size != 18) return
    val cell = min(side / cols, side / rows)
    val gLeft = left + (side - cell * cols) / 2f
    val gTop = top + (side - cell * rows) / 2f
    val pipR = cell * 0.07f
    for (i in 0 until 6) {
        val x = gLeft + hs[i * 3] * cell
        val y = gTop + hs[i * 3 + 1] * cell
        val v = hs[i * 3 + 2]
        if (v == query) {
            drawRect(accent.copy(alpha = 0.35f), topLeft = Offset(x, y), size = Size(cell, cell))
        }
        drawRect(ink, topLeft = Offset(x, y), size = Size(cell, cell), style = Stroke(width = 3f))
        for ((fx, fy) in dicePips(v)) {
            drawCircle(ink, radius = pipR, center = Offset(x + fx * cell, y + fy * cell))
        }
    }
}

/** 삼각형 개수 세기 부채꼴 — 큰 삼각형 + 꼭짓점에서 밑변으로 그은 k개의 선. */
private fun DrawScope.drawTriangleFan(
    figure: ProblemFigure,
    ink: Color,
    accent: Color,
    left: Float,
    top: Float,
    side: Float,
) {
    val k = (figure.params["cevians"] ?: 2).coerceIn(1, 24)
    val apex = Offset(left + side / 2f, top + side * 0.06f)
    val baseY = top + side * 0.94f
    val blX = left + side * 0.06f
    val brX = left + side * 0.94f
    for (i in 1..k) {
        val footX = blX + (brX - blX) * i / (k + 1)
        drawLine(accent, apex, Offset(footX, baseY), strokeWidth = 2f)
    }
    val outline =
        Path().apply {
            moveTo(apex.x, apex.y)
            lineTo(blX, baseY)
            lineTo(brX, baseY)
            close()
        }
    drawPath(outline, color = ink, style = Stroke(width = 4f))
}

/** 격자 위 색칠 다각형(넓이 문제). 옅은 모눈 + 반투명 채움 + 외곽선. */
private fun DrawScope.drawGridPolygon(
    figure: ProblemFigure,
    ink: Color,
    accent: Color,
    left: Float,
    top: Float,
    side: Float,
) {
    val cols = (figure.params["cols"] ?: 4).coerceIn(1, 24)
    val rows = (figure.params["rows"] ?: 4).coerceIn(1, 24)
    val n = (figure.params["n"] ?: 3).coerceIn(3, 24)
    val pts = figure.heights
    if (pts.size != n * 2) return
    val cell = min(side / cols, side / rows)
    val gLeft = left + (side - cell * cols) / 2f
    val gTop = top + (side - cell * rows) / 2f
    val gridColor = ink.copy(alpha = 0.28f)
    for (i in 0..cols) {
        drawLine(gridColor, Offset(gLeft + i * cell, gTop), Offset(gLeft + i * cell, gTop + rows * cell), strokeWidth = 1.5f)
    }
    for (j in 0..rows) {
        drawLine(gridColor, Offset(gLeft, gTop + j * cell), Offset(gLeft + cols * cell, gTop + j * cell), strokeWidth = 1.5f)
    }
    val poly =
        Path().apply {
            moveTo(gLeft + pts[0] * cell, gTop + pts[1] * cell)
            for (i in 1 until n) lineTo(gLeft + pts[i * 2] * cell, gTop + pts[i * 2 + 1] * cell)
            close()
        }
    drawPath(poly, color = accent.copy(alpha = 0.30f))
    drawPath(poly, color = accent, style = Stroke(width = 4f))
}

/** 쌓기나무 등각 투영 좌표. */
private data class IsoView(
    val ox: Float,
    val oy: Float,
    val hw: Float,
    val hh: Float,
    val ch: Float,
) {
    fun proj(
        gx: Float,
        gy: Float,
        gz: Float,
    ) = Offset(ox + (gx - gy) * hw, oy + (gx + gy) * hh - gz * ch)
}

private fun DrawScope.drawIsoFace(
    pts: List<Offset>,
    fill: Color,
    ink: Color,
) {
    val path =
        Path().apply {
            moveTo(pts[0].x, pts[0].y)
            for (k in 1 until pts.size) lineTo(pts[k].x, pts[k].y)
            close()
        }
    drawPath(path, color = fill)
    drawPath(path, color = ink, style = Stroke(width = 2.5f))
}

/** 큐브 하나의 보이는 세 면(윗·오른·왼)을 그린다. */
private fun DrawScope.drawStackCube(
    view: IsoView,
    c: Float,
    r: Float,
    l: Float,
    faceColors: List<Color>,
    ink: Color,
) {
    drawIsoFace(listOf(view.proj(c, r, l + 1), view.proj(c + 1, r, l + 1), view.proj(c + 1, r + 1, l + 1), view.proj(c, r + 1, l + 1)), faceColors[0], ink)
    drawIsoFace(listOf(view.proj(c + 1, r, l + 1), view.proj(c + 1, r + 1, l + 1), view.proj(c + 1, r + 1, l), view.proj(c + 1, r, l)), faceColors[1], ink)
    drawIsoFace(listOf(view.proj(c, r + 1, l + 1), view.proj(c + 1, r + 1, l + 1), view.proj(c + 1, r + 1, l), view.proj(c, r + 1, l)), faceColors[2], ink)
}

/** 쌓기나무를 등각 투영으로 그린다. 뒤→앞·아래→위 순으로 채워 앞 큐브가 뒤를 가린다. */
private fun DrawScope.drawCubeStack(
    figure: ProblemFigure,
    ink: Color,
    faceColors: List<Color>,
    left: Float,
    top: Float,
    side: Float,
) {
    val w = (figure.params["w"] ?: 1).coerceIn(1, 12)
    val d = (figure.params["d"] ?: 1).coerceIn(1, 12)
    val heights = figure.heights
    if (heights.size != w * d) return
    val maxH = (heights.maxOrNull() ?: 1).coerceAtLeast(1)
    val u = side * 0.9f / maxOf((w + d).toFloat(), (w + d) / 2f + maxH)
    val ox = left + (side - (w + d) * u) / 2f + d * u
    val oy = top + (side - ((w + d) * u / 2f + maxH * u)) / 2f + maxH * u
    val view = IsoView(ox, oy, u, u / 2f, u)
    for (t in 0..(w + d - 2)) {
        for (c in 0 until w) {
            val r = t - c
            if (r < 0 || r >= d) continue
            for (l in 0 until heights[r * w + c]) drawStackCube(view, c.toFloat(), r.toFloat(), l.toFloat(), faceColors, ink)
        }
    }
}

/** 정n각형을 원에 내접시켜 그린다. diagonals=1이면 대각선도 함께 그린다. */
private fun DrawScope.drawPolygon(
    figure: ProblemFigure,
    ink: Color,
    accent: Color,
    left: Float,
    top: Float,
    side: Float,
) {
    val n = (figure.params["n"] ?: 5).coerceIn(3, 24)
    val center = Offset(left + side / 2f, top + side / 2f)
    val radius = side * 0.42f
    val pts =
        (0 until n).map { i ->
            val a = Math.toRadians(-90.0 + i * 360.0 / n).toFloat()
            center + Offset(cos(a) * radius, sin(a) * radius)
        }
    val path =
        Path().apply {
            moveTo(pts[0].x, pts[0].y)
            for (i in 1 until n) lineTo(pts[i].x, pts[i].y)
            close()
        }
    drawPath(path, color = ink, style = Stroke(width = 4f))
    if ((figure.params["diagonals"] ?: 0) == 1) {
        drawPolygonDiagonals(pts, accent)
    }
}

/** 정다각형의 모든 대각선(변은 제외)을 그린다. */
private fun DrawScope.drawPolygonDiagonals(
    pts: List<Offset>,
    accent: Color,
) {
    val n = pts.size
    for (i in 0 until n) {
        for (j in i + 2 until n) {
            if (i == 0 && j == n - 1) continue // 첫·끝 꼭짓점은 변이라 제외
            drawLine(accent, pts[i], pts[j], strokeWidth = 2f)
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
    // cell이 side에 맞춰 자동 축소되므로 큰 격자도 안전 — 상한을 넉넉히 둔다.
    // (당구대 12×9·15×8, gcdtile 10×4 등을 8로 자르면 정사각형처럼 왜곡됐다. 파이썬 미리보기엔 clamp 없음.)
    val w = (figure.params["w"] ?: 3).coerceIn(1, 30)
    val h = (figure.params["h"] ?: 3).coerceIn(1, 30)
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
    // 지날 수 없는 교차점 — X로 표시(격자 최단경로 장애물 문제).
    val blockX = figure.params["blockX"]
    val blockY = figure.params["blockY"]
    if (blockX != null && blockY != null) {
        val cx = gridLeft + blockX.coerceIn(0, w) * cell
        val cy = gridTop + blockY.coerceIn(0, h) * cell
        val r = cell * 0.22f
        drawLine(ink, Offset(cx - r, cy - r), Offset(cx + r, cy + r), strokeWidth = 6f)
        drawLine(ink, Offset(cx - r, cy + r), Offset(cx + r, cy - r), strokeWidth = 6f)
    }
    // 한 꼭짓점에서 대각선 반대편 꼭짓점까지 그은 대각선(격자 대각선 문제) — 칸은 세지 않게 색칠 없이 선만.
    if ((figure.params["diag"] ?: 0) == 1) {
        drawLine(
            accent,
            Offset(gridLeft, gridTop),
            Offset(gridLeft + w * cell, gridTop + h * cell),
            strokeWidth = 5f,
        )
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
