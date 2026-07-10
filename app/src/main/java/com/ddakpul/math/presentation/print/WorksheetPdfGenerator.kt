package com.ddakpul.math.presentation.print

import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.pdf.PdfDocument
import android.text.Layout
import android.text.StaticLayout
import android.text.TextPaint
import com.ddakpul.math.domain.model.MathArea
import com.ddakpul.math.domain.model.Problem

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
