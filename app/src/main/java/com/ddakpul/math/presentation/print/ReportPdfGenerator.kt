package com.ddakpul.math.presentation.print

import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.RectF
import android.graphics.pdf.PdfDocument
import android.text.TextPaint
import com.ddakpul.math.domain.model.LearningStats
import com.ddakpul.math.domain.model.MathArea
import kotlin.math.roundToInt

/** 리포트 PDF에 찍을 고정 문구 — 리소스 접근은 화면에서 끝내고 생성기는 순수 문자열만 받는다. */
data class ReportTexts(
    val title: String,
    val generatedOn: String,
    /** (라벨, 값) 4쌍 — 이미 지역화된 문자열. 푼 문제·정답률·현재 난이도·연속 학습. */
    val summary: List<Pair<String, String>>,
    val sectionAreaTitle: String,
    val sectionWeakTitle: String,
    val sectionMistakeTitle: String,
    val weakEmpty: String,
    val mistakeEmpty: String,
    /** 오답 해소율 격려 문구(있으면). 없으면 null. */
    val recoveryLine: String?,
    val areaLabels: Map<MathArea, String>,
    val footer: String,
)

/**
 * 부모용 한 장짜리 학습 리포트 PDF 생성기. 화면의 리포트를 종이/파일로 남길 수 있게 한다
 * (안드로이드 인쇄 프레임워크의 'PDF로 저장' 경유). 외부 전송·네트워크 없음 — 온디바이스 완결.
 */
class ReportPdfGenerator(
    private val stats: LearningStats,
    private val texts: ReportTexts,
) {
    private val titlePaint =
        TextPaint().apply {
            textSize = 20f
            isFakeBoldText = true
            color = Color.BLACK
            isAntiAlias = true
        }
    private val metaPaint =
        TextPaint().apply {
            textSize = 10f
            color = Color.GRAY
            isAntiAlias = true
        }
    private val sectionPaint =
        TextPaint().apply {
            textSize = 13f
            isFakeBoldText = true
            color = Color.DKGRAY
            isAntiAlias = true
        }
    private val labelPaint =
        TextPaint().apply {
            textSize = 10f
            color = Color.GRAY
            isAntiAlias = true
        }
    private val valuePaint =
        TextPaint().apply {
            textSize = 17f
            isFakeBoldText = true
            color = Color.BLACK
            isAntiAlias = true
        }
    private val bodyPaint =
        TextPaint().apply {
            textSize = 12f
            color = Color.BLACK
            isAntiAlias = true
        }
    private val dividerPaint =
        Paint().apply {
            strokeWidth = 1f
            color = Color.LTGRAY
        }
    private val barBgPaint =
        Paint().apply {
            style = Paint.Style.FILL
            color = Color.rgb(0xEC, 0xEF, 0xF4)
            isAntiAlias = true
        }
    private val barFgPaint =
        Paint().apply {
            style = Paint.Style.FILL
            color = Color.rgb(0x4C, 0x6E, 0xF5)
            isAntiAlias = true
        }

    fun generate(): PdfDocument {
        val doc = PdfDocument()
        val info = PdfDocument.PageInfo.Builder(PAGE_WIDTH, PAGE_HEIGHT, 1).create()
        val page = doc.startPage(info)
        val canvas = page.canvas

        var y = drawHeader(canvas)
        y = drawSummary(canvas, y)
        y = drawAreaSection(canvas, y)
        y = drawWeakSection(canvas, y)
        drawMistakeSection(canvas, y)
        drawFooter(canvas)

        doc.finishPage(page)
        return doc
    }

    private fun drawHeader(canvas: Canvas): Float {
        var y = MARGIN.toFloat()
        canvas.drawText(texts.title, MARGIN.toFloat(), y + titlePaint.textSize, titlePaint)
        val metaWidth = metaPaint.measureText(texts.generatedOn)
        canvas.drawText(texts.generatedOn, PAGE_WIDTH - MARGIN - metaWidth, y + titlePaint.textSize, metaPaint)
        y += titlePaint.textSize + 12f
        canvas.drawLine(MARGIN.toFloat(), y, (PAGE_WIDTH - MARGIN).toFloat(), y, dividerPaint)
        return y + 22f
    }

    private fun drawSummary(
        canvas: Canvas,
        top: Float,
    ): Float {
        val items = texts.summary
        if (items.isEmpty()) return top
        val colWidth = CONTENT_WIDTH / items.size.toFloat()
        items.forEachIndexed { i, (label, value) ->
            val x = MARGIN + colWidth * i
            canvas.drawText(label, x, top, labelPaint)
            canvas.drawText(value, x, top + valuePaint.textSize + 4f, valuePaint)
        }
        return top + valuePaint.textSize + 30f
    }

    private fun drawAreaSection(
        canvas: Canvas,
        top: Float,
    ): Float {
        var y = drawSectionTitle(canvas, texts.sectionAreaTitle, top)
        val labelColWidth = 96f
        val statColWidth = 78f
        val barX = MARGIN + labelColWidth
        val barWidth = CONTENT_WIDTH - labelColWidth - statColWidth
        MathArea.entries.forEach { area ->
            val stat = stats.areaStats.firstOrNull { it.area == area }
            val solved = stat?.solved ?: 0
            val correct = stat?.correct ?: 0
            val acc = stat?.accuracy ?: 0f
            val label = texts.areaLabels[area] ?: area.name
            canvas.drawText(label, MARGIN.toFloat(), y + bodyPaint.textSize, bodyPaint)
            val barTop = y + 3f
            val barBottom = y + 15f
            canvas.drawRoundRect(RectF(barX, barTop, barX + barWidth, barBottom), 4f, 4f, barBgPaint)
            if (solved > 0) {
                canvas.drawRoundRect(RectF(barX, barTop, barX + barWidth * acc, barBottom), 4f, 4f, barFgPaint)
            }
            val stextValue = if (solved == 0) "-" else "${(acc * 100).roundToInt()}% ($correct/$solved)"
            canvas.drawText(stextValue, barX + barWidth + 8f, y + bodyPaint.textSize, labelPaint)
            y += 24f
        }
        return y + 12f
    }

    private fun drawWeakSection(
        canvas: Canvas,
        top: Float,
    ): Float {
        var y = drawSectionTitle(canvas, texts.sectionWeakTitle, top)
        val weak =
            stats.conceptStats
                .filter { it.solved >= MIN_CONCEPT_SOLVED }
                .sortedBy { it.accuracy }
                .take(MAX_WEAK)
        if (weak.isEmpty()) {
            canvas.drawText(texts.weakEmpty, MARGIN.toFloat(), y + bodyPaint.textSize, labelPaint)
            return y + 26f
        }
        weak.forEach { c ->
            val line = "• ${c.concept} — ${(c.accuracy * 100).roundToInt()}% (${c.correct}/${c.solved})"
            canvas.drawText(ellipsize(line, CONTENT_WIDTH.toFloat(), bodyPaint), MARGIN.toFloat(), y + bodyPaint.textSize, bodyPaint)
            y += 20f
        }
        return y + 12f
    }

    private fun drawMistakeSection(
        canvas: Canvas,
        top: Float,
    ): Float {
        var y = drawSectionTitle(canvas, texts.sectionMistakeTitle, top)
        val mistakes = stats.recentMistakes.take(MAX_MISTAKES)
        if (mistakes.isEmpty()) {
            canvas.drawText(texts.mistakeEmpty, MARGIN.toFloat(), y + bodyPaint.textSize, labelPaint)
            y += 26f
        } else {
            mistakes.forEach { p ->
                val line = "• ${p.statement}"
                canvas.drawText(ellipsize(line, CONTENT_WIDTH.toFloat(), bodyPaint), MARGIN.toFloat(), y + bodyPaint.textSize, bodyPaint)
                y += 20f
            }
            y += 6f
        }
        texts.recoveryLine?.let {
            canvas.drawText(ellipsize(it, CONTENT_WIDTH.toFloat(), metaPaint), MARGIN.toFloat(), y + metaPaint.textSize, metaPaint)
        }
        return y
    }

    private fun drawSectionTitle(
        canvas: Canvas,
        title: String,
        top: Float,
    ): Float {
        canvas.drawText(title, MARGIN.toFloat(), top + sectionPaint.textSize, sectionPaint)
        return top + sectionPaint.textSize + 10f
    }

    private fun drawFooter(canvas: Canvas) {
        val width = metaPaint.measureText(texts.footer)
        canvas.drawText(texts.footer, (PAGE_WIDTH - width) / 2f, (PAGE_HEIGHT - MARGIN / 2).toFloat(), metaPaint)
    }

    /** 한 줄에 안 들어가면 말줄임(…) 처리. */
    private fun ellipsize(
        text: String,
        maxWidth: Float,
        paint: TextPaint,
    ): String {
        if (paint.measureText(text) <= maxWidth) return text
        val ellipsis = "…"
        var end = text.length
        while (end > 0 && paint.measureText(text.substring(0, end) + ellipsis) > maxWidth) {
            end--
        }
        return text.substring(0, end).trimEnd() + ellipsis
    }

    companion object {
        // A4 (포인트, 72dpi)
        private const val PAGE_WIDTH = 595
        private const val PAGE_HEIGHT = 842
        private const val MARGIN = 40
        private const val CONTENT_WIDTH = PAGE_WIDTH - MARGIN * 2
        private const val MIN_CONCEPT_SOLVED = 2
        private const val MAX_WEAK = 3
        private const val MAX_MISTAKES = 6
    }
}
