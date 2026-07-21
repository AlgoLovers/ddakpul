package com.ddakpul.math.presentation.puzzle

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.ddakpul.math.R
import com.ddakpul.math.domain.model.Cell
import com.ddakpul.math.domain.model.DissectionPuzzle
import com.ddakpul.math.domain.usecase.DissectionError
import com.ddakpul.math.domain.usecase.DissectionValidation

/** 조각 색 팔레트(퍼즐 말). 게임 말 색이라 디자인 토큰과 별개로 고정(라이트·다크 공통). */
val PIECE_COLORS: List<Color> =
    listOf(Color(0xFFFFC078), Color(0xFF63D2A5), Color(0xFFFF8C8C), Color(0xFF74A9FF))

private data class SymbolGlyph(
    val glyph: String,
    val color: Color,
)

private fun symbolOf(code: String): SymbolGlyph =
    when (code) {
        "O" -> SymbolGlyph("●", Color(0xFFE84C46))
        "T" -> SymbolGlyph("▲", Color(0xFF12B26E))
        "S" -> SymbolGlyph("■", Color(0xFF4C8DF6))
        else -> SymbolGlyph(code, Color(0xFF191F28))
    }

/** 등분 검증 실패 사유 → 지역화된 힌트 문구. */
@Composable
fun dissectionHint(error: DissectionError?): String =
    stringResource(
        when (error) {
            DissectionError.INCOMPLETE -> R.string.puzzle_err_incomplete
            DissectionError.WRONG_PIECE_COUNT -> R.string.puzzle_err_count
            DissectionError.UNEQUAL_SIZE -> R.string.puzzle_err_size
            DissectionError.DISCONNECTED -> R.string.puzzle_err_disconnected
            DissectionError.NOT_CONGRUENT -> R.string.puzzle_err_congruent
            DissectionError.SYMBOL -> R.string.puzzle_err_symbol
            null -> R.string.puzzle_err_incomplete
        },
    )

/** 지우기·확인 버튼 줄 — 등분 퍼즐 두 진입점(본 풀이·파일럿) 공용. */
@Composable
fun DissectionControls(
    onClear: () -> Unit,
    onCheck: () -> Unit,
) {
    Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
        OutlinedButton(onClick = onClear) { Text(stringResource(R.string.puzzle_clear)) }
        Button(onClick = onCheck) { Text(stringResource(R.string.puzzle_check)) }
    }
}

/** 검증 결과 메시지(정답=secondary / 오답·미완성 힌트=error) — 두 진입점 공용. '다음' 버튼은 호출부가 조건대로. */
@Composable
fun DissectionResultText(result: DissectionValidation?) {
    val (msg, color) =
        if (result?.isValid == true) {
            stringResource(R.string.puzzle_correct) to MaterialTheme.colorScheme.secondary
        } else {
            dissectionHint(result?.error) to MaterialTheme.colorScheme.error
        }
    Text(text = msg, color = color, fontWeight = FontWeight.Bold, style = MaterialTheme.typography.titleMedium)
}

/** 격자 탭 입력판 — 영역 칸만 그리고, 탭하면 선택한 조각 색으로 칠한다(공용). */
@Composable
fun DissectionBoard(
    puzzle: DissectionPuzzle,
    assignment: Map<Cell, Int>,
    onTap: (Cell) -> Unit,
) {
    val rows = puzzle.cells.maxOf { it.row } + 1
    val cols = puzzle.cells.maxOf { it.col } + 1
    val region = puzzle.cells.toSet()
    val cellSize = 52.dp
    val border = MaterialTheme.colorScheme.outline
    // 안 칠한 칸은 테마 표면색 — 다크에선 어두워 테두리로만 보이고, 칠한 파스텔 조각이 도드라진다.
    val unsetColor = MaterialTheme.colorScheme.surface
    Column {
        for (r in 0 until rows) {
            Row {
                for (c in 0 until cols) {
                    val cell = Cell(r, c)
                    if (cell in region) {
                        val pieceId = assignment[cell]
                        val fill = pieceId?.let { PIECE_COLORS[it % PIECE_COLORS.size] } ?: unsetColor
                        Box(
                            modifier =
                                Modifier
                                    .size(cellSize)
                                    .background(fill)
                                    .border(1.dp, border)
                                    .clickable { onTap(cell) },
                            contentAlignment = Alignment.Center,
                        ) {
                            puzzle.symbols?.get(cell)?.let {
                                val sym = symbolOf(it)
                                Text(text = sym.glyph, color = sym.color, style = MaterialTheme.typography.titleLarge)
                            }
                        }
                    } else {
                        Spacer(Modifier.size(cellSize))
                    }
                }
            }
        }
    }
}

/** 칠할 조각 색 선택 팔레트(공용). */
@Composable
fun PiecePalette(
    pieceCount: Int,
    selected: Int,
    onSelect: (Int) -> Unit,
) {
    Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
        for (id in 0 until pieceCount) {
            val isSel = id == selected
            Box(
                modifier =
                    Modifier
                        .size(if (isSel) 44.dp else 38.dp)
                        .background(PIECE_COLORS[id % PIECE_COLORS.size], CircleShape)
                        .border(
                            width = if (isSel) 3.dp else 1.dp,
                            color = if (isSel) MaterialTheme.colorScheme.onSurface else MaterialTheme.colorScheme.outline,
                            shape = CircleShape,
                        ).clickable { onSelect(id) },
            )
        }
    }
}
