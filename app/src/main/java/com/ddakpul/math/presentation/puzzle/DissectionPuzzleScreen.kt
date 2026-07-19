package com.ddakpul.math.presentation.puzzle

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.Button
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.ddakpul.math.R
import com.ddakpul.math.domain.model.Cell
import com.ddakpul.math.domain.model.DissectionPuzzle
import com.ddakpul.math.domain.usecase.DissectionError

/** 조각 색 팔레트(퍼즐 말)와 심볼 색. 게임 말 색이라 디자인 토큰과 별개로 고정(라이트·다크 공통). */
private val PIECE_COLORS =
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

@Composable
fun DissectionPuzzleScreen(
    onBack: () -> Unit,
    modifier: Modifier = Modifier,
    viewModel: DissectionPuzzleViewModel = hiltViewModel(),
) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()
    Column(
        modifier = modifier.fillMaxSize().padding(20.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(18.dp),
    ) {
        Row(
            modifier = Modifier.widthIn(max = 520.dp).fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            IconButton(onClick = onBack) {
                Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = null)
            }
            Text(
                text = stringResource(R.string.puzzle_title),
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.weight(1f),
            )
            Text(
                text = stringResource(R.string.puzzle_progress, state.index + 1, state.total),
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }

        Text(
            text = state.pilot.prompt,
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.onSurface,
            modifier = Modifier.widthIn(max = 520.dp).fillMaxWidth(),
        )

        PuzzleBoard(
            puzzle = state.pilot.puzzle,
            assignment = state.assignment,
            onTap = viewModel::tapCell,
        )

        PiecePalette(
            pieceCount = state.pilot.puzzle.pieceCount,
            selected = state.selectedPiece,
            onSelect = viewModel::selectPiece,
        )

        Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            OutlinedButton(onClick = viewModel::clear) { Text(stringResource(R.string.puzzle_clear)) }
            Button(onClick = viewModel::check) { Text(stringResource(R.string.puzzle_check)) }
        }

        state.result?.let { result ->
            val (msg, color) =
                if (result.isValid) {
                    stringResource(R.string.puzzle_correct) to MaterialTheme.colorScheme.secondary
                } else {
                    hintFor(result.error) to MaterialTheme.colorScheme.error
                }
            Text(text = msg, color = color, fontWeight = FontWeight.Bold, style = MaterialTheme.typography.titleMedium)
            if (result.isValid) {
                Button(onClick = viewModel::next) { Text(stringResource(R.string.puzzle_next)) }
            }
        }
    }
}

@Composable
private fun hintFor(error: DissectionError?): String =
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

/** 격자 탭 입력판 — 영역 칸만 그리고, 탭하면 선택한 조각 색으로 칠한다. */
@Composable
private fun PuzzleBoard(
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

/** 칠할 조각 색 선택 팔레트. */
@Composable
private fun PiecePalette(
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
