package com.ddakpul.math.presentation.print

import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.Path
import android.graphics.pdf.PdfDocument
import android.text.Layout
import android.text.StaticLayout
import android.text.TextPaint
import com.ddakpul.math.domain.model.FigureType
import com.ddakpul.math.domain.model.MathArea
import com.ddakpul.math.domain.model.Problem
import com.ddakpul.math.domain.model.ProblemFigure
import kotlin.math.cos
import kotlin.math.min
import kotlin.math.sin

/** PDF에 찍을 고정 문구 — 리소스 접근을 화면에서 끝내고 생성기는 순수 문자열만 받는다. */
data class WorksheetTexts(
    val title: String,
    val nameLine: String,
    val dateLine: String,
    val answerTitle: String,
    val footer: String,
    val solutionSpaceLabel: String,
    val areaLabels: Map<MathArea, String>,
)

// A4 (포인트, 72dpi)
private const val PAGE_WIDTH = 595
private const val PAGE_HEIGHT = 842
private const val MARGIN = 40
private const val CONTENT_WIDTH = PAGE_WIDTH - MARGIN * 2
private const val FOOTER_SPACE = 30
private const val SOLUTION_BOX_HEIGHT = 74
private const val BLOCK_SPACING = 18
private const val CIRCLED_ONE = '①' // ①

/**
 * 학습지 PDF 생성기. 구몬식 관례를 따른다 — 헤더에 이름·날짜 기록란,
 * 문항 바로 아래 풀이 공간, 정답·해설은 별지(마지막 장)로 분리.
 */
class WorksheetPdfGenerator(
    private val problems: List<Problem>,
    private val includeAnswers: Boolean,
    private val texts: WorksheetTexts,
) {
    private val titlePaint =
        TextPaint().apply {
            textSize = 18f
            isFakeBoldText = true
            color = Color.BLACK
            isAntiAlias = true
        }
    private val headerPaint =
        TextPaint().apply {
            textSize = 11f
            color = Color.DKGRAY
            isAntiAlias = true
        }
    private val tagPaint =
        TextPaint().apply {
            textSize = 10f
            color = Color.GRAY
            isAntiAlias = true
        }
    private val numberPaint =
        TextPaint().apply {
            textSize = 13f
            isFakeBoldText = true
            color = Color.BLACK
            isAntiAlias = true
        }
    private val bodyPaint =
        TextPaint().apply {
            textSize = 13f
            color = Color.BLACK
            isAntiAlias = true
        }
    private val choicePaint =
        TextPaint().apply {
            textSize = 12f
            color = Color.BLACK
            isAntiAlias = true
        }
    private val captionPaint =
        TextPaint().apply {
            textSize = 9f
            color = Color.GRAY
            isAntiAlias = true
        }
    private val boxPaint =
        Paint().apply {
            style = Paint.Style.STROKE
            strokeWidth = 0.8f
            color = Color.LTGRAY
            isAntiAlias = true
        }
    private val dividerPaint =
        Paint().apply {
            strokeWidth = 1f
            color = Color.DKGRAY
        }

    private var pageNumber = 0

    fun generate(): PdfDocument {
        val doc = PdfDocument()
        var page = newPage(doc)
        var y = drawHeader(page.canvas)

        problems.forEachIndexed { index, problem ->
            val blockHeight = measureProblemBlock(problem)
            if (y + blockHeight > PAGE_HEIGHT - MARGIN - FOOTER_SPACE) {
                finishPage(doc, page)
                page = newPage(doc)
                y = MARGIN.toFloat()
            }
            y = drawProblemBlock(page.canvas, problem, index, y)
        }
        finishPage(doc, page)

        if (includeAnswers) {
            drawAnswerPages(doc)
        }
        return doc
    }

    private fun newPage(doc: PdfDocument): PdfDocument.Page {
        pageNumber++
        val info = PdfDocument.PageInfo.Builder(PAGE_WIDTH, PAGE_HEIGHT, pageNumber).create()
        return doc.startPage(info)
    }

    private fun finishPage(
        doc: PdfDocument,
        page: PdfDocument.Page,
    ) {
        drawFooter(page.canvas)
        doc.finishPage(page)
    }

    /** @return 헤더 아래의 시작 y */
    private fun drawHeader(canvas: Canvas): Float {
        var y = MARGIN.toFloat()
        canvas.drawText(texts.title, MARGIN.toFloat(), y + titlePaint.textSize, titlePaint)
        val nameLine = "${texts.nameLine}        ${texts.dateLine}"
        val nameWidth = headerPaint.measureText(nameLine)
        canvas.drawText(nameLine, PAGE_WIDTH - MARGIN - nameWidth, y + titlePaint.textSize, headerPaint)
        y += titlePaint.textSize + 14f
        canvas.drawLine(MARGIN.toFloat(), y, (PAGE_WIDTH - MARGIN).toFloat(), y, dividerPaint)
        return y + 16f
    }

    private fun drawFooter(canvas: Canvas) {
        val label = "${texts.footer} · $pageNumber"
        val width = captionPaint.measureText(label)
        canvas.drawText(label, (PAGE_WIDTH - width) / 2f, (PAGE_HEIGHT - MARGIN / 2).toFloat(), captionPaint)
    }

    private fun buildLayout(
        text: String,
        paint: TextPaint,
        width: Int = CONTENT_WIDTH,
    ): StaticLayout =
        StaticLayout.Builder
            .obtain(text, 0, text.length, paint, width)
            .setAlignment(Layout.Alignment.ALIGN_NORMAL)
            .setLineSpacing(0f, 1.35f)
            .build()

    private fun choiceLines(problem: Problem): List<String> = problem.choices.mapIndexed { index, choice -> "${CIRCLED_ONE + index} $choice" }

    private fun measureProblemBlock(problem: Problem): Float {
        var height = tagPaint.textSize + 6f
        height += buildLayout(statementText(problem), bodyPaint).height.toFloat() + 8f
        if (problem.figure != null) height += FIGURE_SIZE + 8f
        choiceLines(problem).forEach { line ->
            height += buildLayout(line, choicePaint, CONTENT_WIDTH - 12).height.toFloat() + 2f
        }
        height += 8f + SOLUTION_BOX_HEIGHT + BLOCK_SPACING
        return height
    }

    private fun statementText(problem: Problem): String = problem.statement

    /** @return 블록 아래의 다음 y */
    private fun drawProblemBlock(
        canvas: Canvas,
        problem: Problem,
        index: Int,
        startY: Float,
    ): Float {
        var y = startY
        val areaLabel = texts.areaLabels[problem.area].orEmpty()

        // 번호 + 영역·난이도 태그
        val numberText = "${index + 1}."
        canvas.drawText(numberText, MARGIN.toFloat(), y + numberPaint.textSize, numberPaint)
        val tag = "$areaLabel · Lv.${problem.difficulty}"
        val tagWidth = tagPaint.measureText(tag)
        canvas.drawText(tag, PAGE_WIDTH - MARGIN - tagWidth, y + numberPaint.textSize, tagPaint)
        y += tagPaint.textSize + 6f

        // 문제 지문
        val statementLayout = buildLayout(statementText(problem), bodyPaint)
        canvas.withTranslate(MARGIN.toFloat(), y) { statementLayout.draw(this) }
        y += statementLayout.height + 8f

        // 도형 지시서 — 화면과 같은 그림을 인쇄물에도 그린다.
        problem.figure?.let { figure ->
            drawFigure(canvas, figure, PAGE_WIDTH / 2f, y, FIGURE_SIZE)
            y += FIGURE_SIZE + 8f
        }

        // 보기 ①~④
        choiceLines(problem).forEach { line ->
            val layout = buildLayout(line, choicePaint, CONTENT_WIDTH - 12)
            canvas.withTranslate(MARGIN + 12f, y) { layout.draw(this) }
            y += layout.height + 2f
        }
        y += 8f

        // 풀이 공간 — 문항 바로 아래에 두면 시작·완료율이 올라간다.
        canvas.drawRoundRect(
            MARGIN.toFloat(),
            y,
            (PAGE_WIDTH - MARGIN).toFloat(),
            y + SOLUTION_BOX_HEIGHT,
            6f,
            6f,
            boxPaint,
        )
        canvas.drawText(texts.solutionSpaceLabel, MARGIN + 8f, y + captionPaint.textSize + 6f, captionPaint)
        y += SOLUTION_BOX_HEIGHT + BLOCK_SPACING
        return y
    }

    private fun drawAnswerPages(doc: PdfDocument) {
        var page = newPage(doc)
        var canvas = page.canvas
        var y = MARGIN.toFloat()
        canvas.drawText(texts.answerTitle, MARGIN.toFloat(), y + titlePaint.textSize, titlePaint)
        y += titlePaint.textSize + 14f
        canvas.drawLine(MARGIN.toFloat(), y, (PAGE_WIDTH - MARGIN).toFloat(), y, dividerPaint)
        y += 16f

        problems.forEachIndexed { index, problem ->
            val answerChar = CIRCLED_ONE + problem.answer.correctChoiceIndex
            val answerLine = "${index + 1}. $answerChar ${problem.choices[problem.answer.correctChoiceIndex]}"
            val answerLayout = buildLayout(answerLine, numberPaint)
            val explanationLayout = problem.explanation?.let { buildLayout(it, headerPaint, CONTENT_WIDTH - 16) }
            val blockHeight =
                answerLayout.height + (explanationLayout?.height?.plus(4) ?: 0) + 12f

            if (y + blockHeight > PAGE_HEIGHT - MARGIN - FOOTER_SPACE) {
                finishPage(doc, page)
                page = newPage(doc)
                canvas = page.canvas
                y = MARGIN.toFloat()
            }

            canvas.withTranslate(MARGIN.toFloat(), y) { answerLayout.draw(this) }
            y += answerLayout.height.toFloat()
            explanationLayout?.let { layout ->
                y += 4f
                canvas.withTranslate(MARGIN + 16f, y) { layout.draw(this) }
                y += layout.height
            }
            y += 12f
        }
        finishPage(doc, page)
    }
}

private const val FIGURE_SIZE = 110f

/** 도형 지시서를 PDF 캔버스에 그린다 — 화면 렌더러(ProblemFigureView)와 같은 수식. */
private fun drawFigure(
    canvas: Canvas,
    figure: ProblemFigure,
    centerX: Float,
    top: Float,
    size: Float,
) {
    val ink =
        Paint().apply {
            color = Color.BLACK
            style = Paint.Style.STROKE
            strokeWidth = 1.4f
            isAntiAlias = true
        }
    val fill =
        Paint().apply {
            color = Color.BLACK
            style = Paint.Style.FILL
            isAntiAlias = true
        }
    when (figure.type) {
        FigureType.CLOCK -> drawPdfClock(canvas, figure, centerX, top, size, ink, fill)
        FigureType.DOT_BORDER -> drawPdfDotBorder(canvas, figure, centerX, top, size, fill)
        FigureType.GRID -> drawPdfGrid(canvas, figure, centerX, top, size, ink, fill)
        FigureType.L_SHAPE -> drawPdfLShape(canvas, figure, centerX, top, size, ink)
        FigureType.POLYGON -> drawPdfPolygon(canvas, figure, centerX, top, size, ink)
        FigureType.CUBE_STACK -> drawPdfCubeStack(canvas, figure, centerX, top, size)
        FigureType.GRID_POLYGON -> drawPdfGridPolygon(canvas, figure, centerX, top, size, ink)
        FigureType.TRIANGLE_FAN -> drawPdfTriangleFan(canvas, figure, centerX, top, size, ink)
        FigureType.CUBE_NET -> drawPdfCubeNet(canvas, figure, centerX, top, size, ink, fill)
        FigureType.MATCHSTICK -> drawPdfMatchstick(canvas, figure, centerX, top, size, ink)
        FigureType.BAR_CHART -> drawPdfBarChart(canvas, figure, centerX, top, size, ink)
    }
}

/** 막대그래프 — heights의 값을 막대로, 위에 값·아래에 범주(가·나·다…)를 찍는다. */
private fun drawPdfBarChart(
    canvas: Canvas,
    figure: ProblemFigure,
    centerX: Float,
    top: Float,
    size: Float,
    ink: Paint,
) {
    val values = figure.heights
    if (values.isEmpty()) return
    val n = values.size
    val maxV = (values.maxOrNull() ?: 1).coerceAtLeast(1)
    val highlight = figure.params["highlight"] ?: -1
    val left = centerX - size / 2f
    val base = top + size * 0.86f
    val chartH = size * 0.66f
    val slot = size / n
    val barW = slot * 0.54f
    canvas.drawLine(left, base, left + size, base, ink)
    val barPaint =
        Paint().apply {
            color = Color.rgb(70, 100, 200)
            style = Paint.Style.FILL
            isAntiAlias = true
        }
    val hiPaint =
        Paint().apply {
            color = Color.BLACK
            style = Paint.Style.FILL
            isAntiAlias = true
        }
    val labelPaint =
        TextPaint().apply {
            textSize = 9f
            color = Color.DKGRAY
            isAntiAlias = true
            textAlign = Paint.Align.CENTER
        }
    val labels = "가나다라마바사아"
    for (i in 0 until n) {
        val cx = left + slot * (i + 0.5f)
        val barH = chartH * values[i] / maxV
        canvas.drawRect(cx - barW / 2f, base - barH, cx + barW / 2f, base, if (i == highlight) hiPaint else barPaint)
        canvas.drawText(values[i].toString(), cx, base - barH - 4f, labelPaint)
        canvas.drawText(if (i < labels.length) labels[i].toString() else "${i + 1}", cx, base + 12f, labelPaint)
    }
}

/** 성냥개비로 이어 붙인 정사각형(기본)/정삼각형(tri=1) 한 줄. */
private fun drawPdfMatchstick(
    canvas: Canvas,
    figure: ProblemFigure,
    centerX: Float,
    top: Float,
    size: Float,
    ink: Paint,
) {
    val n = (figure.params["n"] ?: 3).coerceIn(1, 8)
    val isTri = (figure.params["tri"] ?: 0) == 1
    val stick =
        Paint(ink).apply {
            strokeWidth = 3f
            strokeCap = Paint.Cap.ROUND
        }
    if (!isTri) {
        val s = min(size / n, size * 0.5f)
        val gl = centerX - s * n / 2f
        val gt = top + (size - s) / 2f
        canvas.drawLine(gl, gt, gl + s * n, gt, stick)
        canvas.drawLine(gl, gt + s, gl + s * n, gt + s, stick)
        for (i in 0..n) canvas.drawLine(gl + i * s, gt, gl + i * s, gt + s, stick)
    } else {
        val s = min(size * 2f / (n + 1), size * 0.5f)
        val hgt = s * 0.87f
        val totalW = s * (n + 1) / 2f
        val gl = centerX - totalW / 2f
        val baseY = top + (size + hgt) / 2f
        val topY = baseY - hgt

        fun px(k: Int) = gl + k * (s / 2f)

        fun py(k: Int) = if (k % 2 == 0) baseY else topY
        for (i in 0 until n) {
            canvas.drawLine(px(i), py(i), px(i + 1), py(i + 1), stick)
            canvas.drawLine(px(i + 1), py(i + 1), px(i + 2), py(i + 2), stick)
            canvas.drawLine(px(i + 2), py(i + 2), px(i), py(i), stick)
        }
    }
}

/** 주사위 눈(1~6) 위치를 면 내부 비율 좌표(0~1)로. */
private fun pdfPips(v: Int): List<Pair<Float, Float>> =
    when (v) {
        1 -> listOf(0.5f to 0.5f)
        2 -> listOf(0.3f to 0.3f, 0.7f to 0.7f)
        3 -> listOf(0.28f to 0.28f, 0.5f to 0.5f, 0.72f to 0.72f)
        4 -> listOf(0.3f to 0.3f, 0.7f to 0.3f, 0.3f to 0.7f, 0.7f to 0.7f)
        5 -> listOf(0.28f to 0.28f, 0.72f to 0.28f, 0.5f to 0.5f, 0.28f to 0.72f, 0.72f to 0.72f)
        6 -> listOf(0.3f to 0.28f, 0.3f to 0.5f, 0.3f to 0.72f, 0.7f to 0.28f, 0.7f to 0.5f, 0.7f to 0.72f)
        else -> emptyList()
    }

/** 정육면체(주사위) 전개도 — 흑백 인쇄용: 격자에 면·눈을 찍고 색칠 면은 회색으로 강조. */
private fun drawPdfCubeNet(
    canvas: Canvas,
    figure: ProblemFigure,
    centerX: Float,
    top: Float,
    size: Float,
    ink: Paint,
    fill: Paint,
) {
    val cols = (figure.params["cols"] ?: 4).coerceIn(1, 6)
    val rows = (figure.params["rows"] ?: 4).coerceIn(1, 6)
    val query = figure.params["query"] ?: -1
    val hs = figure.heights
    if (hs.size != 18) return
    val cell = min(size / cols, size / rows)
    val gl = centerX - cell * cols / 2f
    val gt = top + (size - cell * rows) / 2f
    val pipR = cell * 0.07f
    val shade =
        Paint().apply {
            style = Paint.Style.FILL
            color = Color.rgb(220, 220, 220)
            isAntiAlias = true
        }
    for (i in 0 until 6) {
        val x = gl + hs[i * 3] * cell
        val y = gt + hs[i * 3 + 1] * cell
        val v = hs[i * 3 + 2]
        if (v == query) canvas.drawRect(x, y, x + cell, y + cell, shade)
        canvas.drawRect(x, y, x + cell, y + cell, ink)
        for ((fx, fy) in pdfPips(v)) canvas.drawCircle(x + fx * cell, y + fy * cell, pipR, fill)
    }
}

/** 삼각형 개수 세기 부채꼴 — 큰 삼각형 + 꼭짓점에서 밑변으로 그은 k개의 선. */
private fun drawPdfTriangleFan(
    canvas: Canvas,
    figure: ProblemFigure,
    centerX: Float,
    top: Float,
    size: Float,
    ink: Paint,
) {
    val k = (figure.params["cevians"] ?: 2).coerceIn(1, 10)
    val apexX = centerX
    val apexY = top + size * 0.06f
    val baseY = top + size * 0.94f
    val blX = centerX - size * 0.44f
    val brX = centerX + size * 0.44f
    val thin = Paint(ink).apply { strokeWidth = 0.8f }
    for (i in 1..k) {
        val footX = blX + (brX - blX) * i / (k + 1)
        canvas.drawLine(apexX, apexY, footX, baseY, thin)
    }
    canvas.drawLine(apexX, apexY, blX, baseY, ink)
    canvas.drawLine(apexX, apexY, brX, baseY, ink)
    canvas.drawLine(blX, baseY, brX, baseY, ink)
}

/** 격자 위 색칠 다각형(넓이 문제) — 흑백 인쇄용: 옅은 모눈 + 회색 채움 + 굵은 외곽선. */
private fun drawPdfGridPolygon(
    canvas: Canvas,
    figure: ProblemFigure,
    centerX: Float,
    top: Float,
    size: Float,
    ink: Paint,
) {
    val cols = (figure.params["cols"] ?: 4).coerceIn(1, 12)
    val rows = (figure.params["rows"] ?: 4).coerceIn(1, 12)
    val n = (figure.params["n"] ?: 3).coerceIn(3, 12)
    val pts = figure.heights
    if (pts.size != n * 2) return
    val cell = min(size / cols, size / rows)
    val gl = centerX - cell * cols / 2f
    val gt = top + (size - cell * rows) / 2f
    val gridPaint =
        Paint(ink).apply {
            strokeWidth = 0.6f
            color = Color.rgb(160, 160, 160)
        }
    for (i in 0..cols) canvas.drawLine(gl + i * cell, gt, gl + i * cell, gt + rows * cell, gridPaint)
    for (j in 0..rows) canvas.drawLine(gl, gt + j * cell, gl + cols * cell, gt + j * cell, gridPaint)
    val path =
        Path().apply {
            moveTo(gl + pts[0] * cell, gt + pts[1] * cell)
            for (i in 1 until n) lineTo(gl + pts[i * 2] * cell, gt + pts[i * 2 + 1] * cell)
            close()
        }
    canvas.drawPath(
        path,
        Paint().apply {
            style = Paint.Style.FILL
            color = Color.rgb(205, 205, 205)
            isAntiAlias = true
        },
    )
    canvas.drawPath(
        path,
        Paint(ink).apply {
            strokeWidth = 1.8f
            color = Color.BLACK
        },
    )
}

private fun drawPdfPolygon(
    canvas: Canvas,
    figure: ProblemFigure,
    centerX: Float,
    top: Float,
    size: Float,
    ink: Paint,
) {
    val n = (figure.params["n"] ?: 5).coerceIn(3, 12)
    val cy = top + size / 2f
    val radius = size * 0.42f
    val xs = FloatArray(n)
    val ys = FloatArray(n)
    for (i in 0 until n) {
        val a = Math.toRadians(-90.0 + i * 360.0 / n)
        xs[i] = centerX + cos(a).toFloat() * radius
        ys[i] = cy + sin(a).toFloat() * radius
    }
    for (i in 0 until n) {
        canvas.drawLine(xs[i], ys[i], xs[(i + 1) % n], ys[(i + 1) % n], ink)
    }
    if ((figure.params["diagonals"] ?: 0) == 1) {
        drawPdfPolygonDiagonals(canvas, xs, ys, Paint(ink).apply { strokeWidth = 0.8f })
    }
}

private fun drawPdfPolygonDiagonals(
    canvas: Canvas,
    xs: FloatArray,
    ys: FloatArray,
    paint: Paint,
) {
    val n = xs.size
    for (i in 0 until n) {
        for (j in i + 2 until n) {
            if (i == 0 && j == n - 1) continue // 첫·끝 꼭짓점은 변이라 제외
            canvas.drawLine(xs[i], ys[i], xs[j], ys[j], paint)
        }
    }
}

private class PdfIso(
    val ox: Float,
    val oy: Float,
    val hw: Float,
    val hh: Float,
    val ch: Float,
) {
    fun px(
        gx: Float,
        gy: Float,
        gz: Float,
    ) = floatArrayOf(ox + (gx - gy) * hw, oy + (gx + gy) * hh - gz * ch)
}

private fun drawPdfIsoFace(
    canvas: Canvas,
    pts: List<FloatArray>,
    fill: Paint,
    outline: Paint,
) {
    val path =
        Path().apply {
            moveTo(pts[0][0], pts[0][1])
            for (k in 1 until pts.size) lineTo(pts[k][0], pts[k][1])
            close()
        }
    canvas.drawPath(path, fill)
    canvas.drawPath(path, outline)
}

private fun drawPdfStackCube(
    canvas: Canvas,
    view: PdfIso,
    c: Float,
    r: Float,
    l: Float,
    fills: List<Paint>,
    outline: Paint,
) {
    drawPdfIsoFace(canvas, listOf(view.px(c, r, l + 1), view.px(c + 1, r, l + 1), view.px(c + 1, r + 1, l + 1), view.px(c, r + 1, l + 1)), fills[0], outline)
    drawPdfIsoFace(canvas, listOf(view.px(c + 1, r, l + 1), view.px(c + 1, r + 1, l + 1), view.px(c + 1, r + 1, l), view.px(c + 1, r, l)), fills[1], outline)
    drawPdfIsoFace(canvas, listOf(view.px(c, r + 1, l + 1), view.px(c + 1, r + 1, l + 1), view.px(c + 1, r + 1, l), view.px(c, r + 1, l)), fills[2], outline)
}

private fun drawPdfCubeStack(
    canvas: Canvas,
    figure: ProblemFigure,
    centerX: Float,
    top: Float,
    size: Float,
) {
    val w = (figure.params["w"] ?: 1).coerceIn(1, 6)
    val d = (figure.params["d"] ?: 1).coerceIn(1, 6)
    val heights = figure.heights
    if (heights.size != w * d) return
    val maxH = (heights.maxOrNull() ?: 1).coerceAtLeast(1)
    val u = size * 0.9f / maxOf((w + d).toFloat(), (w + d) / 2f + maxH)
    val ox = centerX - size / 2f + (size - (w + d) * u) / 2f + d * u
    val oy = top + (size - ((w + d) * u / 2f + maxH * u)) / 2f + maxH * u
    val view = PdfIso(ox, oy, u, u / 2f, u)
    val outline =
        Paint().apply {
            color = Color.BLACK
            style = Paint.Style.STROKE
            strokeWidth = 1.2f
            isAntiAlias = true
        }
    val fills =
        listOf(255, 228, 205).map { g ->
            Paint().apply {
                color = Color.rgb(g, g, g)
                style = Paint.Style.FILL
                isAntiAlias = true
            }
        }
    for (t in 0..(w + d - 2)) {
        for (c in 0 until w) {
            val r = t - c
            if (r < 0 || r >= d) continue
            for (l in 0 until heights[r * w + c]) drawPdfStackCube(canvas, view, c.toFloat(), r.toFloat(), l.toFloat(), fills, outline)
        }
    }
}

private fun drawPdfClock(
    canvas: Canvas,
    figure: ProblemFigure,
    centerX: Float,
    top: Float,
    size: Float,
    ink: Paint,
    fill: Paint,
) {
    val hour = figure.params["hour"] ?: 12
    val minute = figure.params["minute"] ?: 0
    val cy = top + size / 2f
    val radius = size / 2f
    canvas.drawCircle(centerX, cy, radius, ink)
    for (i in 0 until 12) {
        val angle = Math.toRadians(i * 30.0 - 90)
        val cosA = cos(angle).toFloat()
        val sinA = sin(angle).toFloat()
        canvas.drawLine(
            centerX + cosA * radius * 0.82f,
            cy + sinA * radius * 0.82f,
            centerX + cosA * radius * 0.95f,
            cy + sinA * radius * 0.95f,
            ink,
        )
    }
    val hourAngle = Math.toRadians((hour % 12) * 30 + minute * 0.5 - 90)
    val minAngle = Math.toRadians(minute * 6.0 - 90)
    val bold = Paint(ink).apply { strokeWidth = 3f }
    canvas.drawLine(centerX, cy, centerX + cos(hourAngle).toFloat() * radius * 0.5f, cy + sin(hourAngle).toFloat() * radius * 0.5f, bold)
    canvas.drawLine(centerX, cy, centerX + cos(minAngle).toFloat() * radius * 0.75f, cy + sin(minAngle).toFloat() * radius * 0.75f, ink)
    canvas.drawCircle(centerX, cy, 2.5f, fill)
}

private fun drawPdfDotBorder(
    canvas: Canvas,
    figure: ProblemFigure,
    centerX: Float,
    top: Float,
    size: Float,
    fill: Paint,
) {
    val n = (figure.params["side"] ?: 6).coerceIn(3, 20)
    val left = centerX - size / 2f
    val step = size / (n - 1)
    val r = (step * 0.28f).coerceAtMost(4f)
    for (row in 0 until n) {
        for (col in 0 until n) {
            val onEdge = row % (n - 1) == 0 || col % (n - 1) == 0
            if (onEdge) canvas.drawCircle(left + col * step, top + row * step, r, fill)
        }
    }
}

private fun drawPdfGrid(
    canvas: Canvas,
    figure: ProblemFigure,
    centerX: Float,
    top: Float,
    size: Float,
    ink: Paint,
    fill: Paint,
) {
    val w = (figure.params["w"] ?: 3).coerceIn(1, 8)
    val h = (figure.params["h"] ?: 3).coerceIn(1, 8)
    val cell = min(size / w, size / h)
    val gl = centerX - cell * w / 2f
    val gt = top + (size - cell * h) / 2f
    for (i in 0..w) canvas.drawLine(gl + i * cell, gt, gl + i * cell, gt + h * cell, ink)
    for (j in 0..h) canvas.drawLine(gl, gt + j * cell, gl + w * cell, gt + j * cell, ink)
    if ((figure.params["mark"] ?: 0) == 1) {
        canvas.drawCircle(gl, gt + h * cell, 4f, fill)
        canvas.drawCircle(gl + w * cell, gt, 4f, ink)
    }
    val blockX = figure.params["blockX"]
    val blockY = figure.params["blockY"]
    if (blockX != null && blockY != null) {
        val cx = gl + blockX.coerceIn(0, w) * cell
        val cy = gt + blockY.coerceIn(0, h) * cell
        val r = cell * 0.22f
        val x = Paint(ink).apply { strokeWidth = 2.4f }
        canvas.drawLine(cx - r, cy - r, cx + r, cy + r, x)
        canvas.drawLine(cx - r, cy + r, cx + r, cy - r, x)
    }
    if ((figure.params["diag"] ?: 0) == 1) {
        val diag = Paint(ink).apply { strokeWidth = 2.4f }
        canvas.drawLine(gl, gt, gl + w * cell, gt + h * cell, diag)
    }
}

private fun drawPdfLShape(
    canvas: Canvas,
    figure: ProblemFigure,
    centerX: Float,
    top: Float,
    size: Float,
    ink: Paint,
) {
    val w = (figure.params["w"] ?: 10).toFloat()
    val cutW = (figure.params["cutW"] ?: 4).toFloat()
    val cutH = (figure.params["cutH"] ?: 4).toFloat()
    val left = centerX - size / 2f
    val scale = size / w
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
    canvas.drawPath(path, ink)
    val labelPaint =
        TextPaint().apply {
            textSize = 8f
            color = Color.DKGRAY
            isAntiAlias = true
        }
    canvas.drawText("${w.toInt()}cm", left + w * scale / 2f - 8f, top + w * scale + 10f, labelPaint)
    canvas.drawText("${cutW.toInt()}cm", left + (w - cutW / 2f) * scale - 8f, top + cutH * scale - 4f, labelPaint)
    canvas.drawText("${cutH.toInt()}cm", left + (w - cutW) * scale - 24f, top + cutH * scale / 2f + 3f, labelPaint)
}

/** Canvas 이동을 안전하게 감싸는 헬퍼(save/restore 누락 방지). */
private inline fun Canvas.withTranslate(
    dx: Float,
    dy: Float,
    block: Canvas.() -> Unit,
) {
    val checkpoint = save()
    translate(dx, dy)
    try {
        block()
    } finally {
        restoreToCount(checkpoint)
    }
}
