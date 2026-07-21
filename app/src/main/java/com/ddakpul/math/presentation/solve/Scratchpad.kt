@file:Suppress("MatchingDeclarationName") // 연습장 관련 선언들을 한 파일에 모은다.

package com.ddakpul.math.presentation.solve

import androidx.activity.compose.BackHandler
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.awaitEachGesture
import androidx.compose.foundation.gestures.awaitFirstDown
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.systemBarsPadding
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.runtime.snapshots.SnapshotStateList
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Rect
import androidx.compose.ui.graphics.BlendMode
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Paint
import androidx.compose.ui.graphics.PaintingStyle
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.StrokeJoin
import androidx.compose.ui.graphics.drawscope.drawIntoCanvas
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.ddakpul.math.R
import com.ddakpul.math.core.designsystem.component.ProblemFigureView
import com.ddakpul.math.domain.model.ProblemFigure

/** 한 획(펜 또는 지우개). 지우개 획은 아래 종이/모눈이 드러나도록 잉크만 지운다. */
class ScratchStroke(
    val points: List<Offset>,
    val color: Color,
    val width: Float,
    val eraser: Boolean,
)

private enum class ScratchTool { PEN, ERASER }

/** 문제별로 유지되는 손글씨 상태 — 종이 대신 손가락/펜으로 풀이를 끄적인다. */
@Composable
fun rememberScratchStrokes(problemId: String): SnapshotStateList<ScratchStroke> = remember(problemId) { mutableStateListOf() }

/**
 * 전체화면 디지털 연습장(오버레이). 위에 문제를 작게 고정해 보면서 풀 수 있게 하고, 아래는 모눈 그리기 판.
 * 그린 내용은 [strokes]에 남아 이 문제를 푸는 동안 유지된다(닫았다 열어도 그대로).
 *
 * 별도 Dialog 창이 아니라 본문 위 오버레이라, 태블릿 작업표시줄/네비게이션 바 인셋을 앱 창과 똑같이
 * 존중한다(Dialog 창은 인셋을 전달하지 않아 하단 도구모음이 가려지는 문제가 있었다).
 */
@OptIn(ExperimentalLayoutApi::class)
@Composable
fun ScratchpadOverlay(
    statement: String,
    figure: ProblemFigure?,
    strokes: SnapshotStateList<ScratchStroke>,
    onDismiss: () -> Unit,
    modifier: Modifier = Modifier,
) {
    BackHandler(onBack = onDismiss)
    Surface(modifier = modifier.fillMaxSize(), color = MaterialTheme.colorScheme.surface) {
        Column(modifier = Modifier.fillMaxSize().systemBarsPadding().padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            ScratchHeader(statement = statement, onDismiss = onDismiss)

            var tool by remember { mutableStateOf(ScratchTool.PEN) }
            var penColor by remember { mutableStateOf(InkColors.first()) }

            Box(modifier = Modifier.weight(1f).fillMaxWidth().background(PaperColor, RoundedCornerShape(12.dp))) {
                // 도형 문제면 그림을 연습장 위쪽에 깔아, 그 위에 보조선을 그으며 풀 수 있게 한다.
                figure?.let {
                    ProblemFigureView(figure = it, modifier = Modifier.align(Alignment.TopCenter).padding(top = 8.dp))
                }
                ScratchCanvas(strokes = strokes, tool = tool, penColor = penColor, modifier = Modifier.fillMaxSize())
            }

            // 색 팔레트와 도구 버튼을 각각 한 덩어리로 두고, 폭이 좁거나(소형 폰) 라벨이 긴
            // 로케일(영어)에서 도구 그룹이 둘째 줄로 내려가게 FlowRow로 감싼다. 예전엔 Spacer(weight)
            // 하나로 오른쪽에 붙였는데, 넘칠 때 마지막 버튼("전체 지우기")이 화면 밖으로 잘렸다.
            FlowRow(
                modifier = Modifier.fillMaxWidth().padding(top = 4.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                Row(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    InkColors.forEach { c ->
                        val selected = tool == ScratchTool.PEN && penColor == c
                        Box(
                            modifier =
                                Modifier
                                    .size(if (selected) 40.dp else 32.dp)
                                    .background(c, CircleShape)
                                    .then(if (selected) Modifier.border(3.dp, MaterialTheme.colorScheme.primary, CircleShape) else Modifier)
                                    .clickable {
                                        tool = ScratchTool.PEN
                                        penColor = c
                                    },
                        )
                    }
                }
                Row(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    ToolButton(R.string.scratch_eraser, tool == ScratchTool.ERASER) { tool = ScratchTool.ERASER }
                    ToolButton(R.string.scratch_undo, false) { strokes.removeLastOrNull() }
                    ToolButton(R.string.scratch_clear, false) { strokes.clear() }
                }
            }
        }
    }
}

@Composable
private fun ScratchHeader(
    statement: String,
    onDismiss: () -> Unit,
) {
    Row(verticalAlignment = Alignment.CenterVertically) {
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = stringResource(R.string.scratch_title),
                style = MaterialTheme.typography.labelLarge,
                color = MaterialTheme.colorScheme.primary,
                fontWeight = FontWeight.Bold,
            )
            Text(text = statement, style = MaterialTheme.typography.bodyMedium)
        }
        Text(
            text = "✕",
            style = MaterialTheme.typography.titleLarge,
            modifier = Modifier.clickable(onClick = onDismiss).padding(8.dp),
        )
    }
}

@Composable
private fun ScratchCanvas(
    strokes: SnapshotStateList<ScratchStroke>,
    tool: ScratchTool,
    penColor: Color,
    modifier: Modifier = Modifier,
) {
    val current = remember { mutableStateListOf<Offset>() }
    Canvas(
        modifier =
            modifier.pointerInput(tool, penColor) {
                awaitEachGesture {
                    val down = awaitFirstDown()
                    current.clear()
                    current.add(down.position)
                    down.consume()
                    var active = true
                    while (active) {
                        val change = awaitPointerEvent().changes.firstOrNull { it.id == down.id }
                        if (change != null) {
                            current.add(change.position)
                            change.consume()
                            active = change.pressed
                        } else {
                            active = false
                        }
                    }
                    val eraser = tool == ScratchTool.ERASER
                    strokes.add(
                        ScratchStroke(
                            points = current.toList(),
                            color = if (eraser) Color.Transparent else penColor,
                            width = if (eraser) ERASER_WIDTH else PEN_WIDTH,
                            eraser = eraser,
                        ),
                    )
                    current.clear()
                }
            },
    ) {
        // 모눈(배경) — 지우개가 이 위의 잉크만 지우고 모눈은 유지되게 아래에 깐다.
        val step = 28.dp.toPx()
        var gx = step
        while (gx < size.width) {
            drawLine(GridColor, Offset(gx, 0f), Offset(gx, size.height), 1f)
            gx += step
        }
        var gy = step
        while (gy < size.height) {
            drawLine(GridColor, Offset(0f, gy), Offset(size.width, gy), 1f)
            gy += step
        }
        // 획은 별도 레이어에 그려 지우개(BlendMode.Clear)가 잉크만 투명하게 만든다.
        drawIntoCanvas { canvas ->
            canvas.saveLayer(Rect(Offset.Zero, size), Paint())
            strokes.forEach { drawStroke(canvas, it.points, it.color, it.width, it.eraser) }
            if (current.isNotEmpty()) {
                val eraser = tool == ScratchTool.ERASER
                drawStroke(canvas, current.toList(), if (eraser) Color.Transparent else penColor, if (eraser) ERASER_WIDTH else PEN_WIDTH, eraser)
            }
            canvas.restore()
        }
    }
}

private fun drawStroke(
    canvas: androidx.compose.ui.graphics.Canvas,
    points: List<Offset>,
    color: Color,
    width: Float,
    eraser: Boolean,
) {
    if (points.isEmpty()) return
    val paint =
        Paint().apply {
            style = PaintingStyle.Stroke
            strokeWidth = width
            strokeCap = StrokeCap.Round
            strokeJoin = StrokeJoin.Round
            isAntiAlias = true
            if (eraser) blendMode = BlendMode.Clear else this.color = color
        }
    if (points.size == 1) {
        val dot = Paint().apply { if (eraser) blendMode = BlendMode.Clear else this.color = color }
        canvas.drawCircle(points.first(), width / 2f, dot)
        return
    }
    val path =
        Path().apply {
            moveTo(points.first().x, points.first().y)
            for (i in 1 until points.size) lineTo(points[i].x, points[i].y)
        }
    canvas.drawPath(path, paint)
}

@Composable
private fun ToolButton(
    labelRes: Int,
    active: Boolean,
    onClick: () -> Unit,
) {
    Surface(
        color = if (active) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.surfaceContainerHigh,
        shape = RoundedCornerShape(20.dp),
        modifier = Modifier.clickable(onClick = onClick),
    ) {
        Text(
            text = stringResource(labelRes),
            modifier = Modifier.padding(horizontal = 14.dp, vertical = 8.dp),
            style = MaterialTheme.typography.labelLarge,
            color = if (active) MaterialTheme.colorScheme.onPrimary else MaterialTheme.colorScheme.onSurface,
        )
    }
}

private const val PEN_WIDTH = 5f
private const val ERASER_WIDTH = 42f
private val PaperColor = Color(0xFFFDFBF5) // 따뜻한 종이색
private val GridColor = Color(0x14000000) // 아주 옅은 모눈
private val InkColors = listOf(Color(0xFF222222), Color(0xFF2962FF), Color(0xFFD32F2F)) // 검정·파랑·빨강
