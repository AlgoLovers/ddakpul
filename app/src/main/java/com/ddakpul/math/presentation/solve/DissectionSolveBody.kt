package com.ddakpul.math.presentation.solve

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.ddakpul.math.R
import com.ddakpul.math.domain.model.Cell
import com.ddakpul.math.presentation.puzzle.DissectionBoard
import com.ddakpul.math.presentation.puzzle.PiecePalette
import com.ddakpul.math.presentation.puzzle.dissectionHint

/**
 * 본 풀이 흐름 안의 등분 퍼즐 화면 — 4지선다 [SolvingBody]/[ResultView]에 대응하는 구성형 경로.
 * 격자 탭 입력판 + 조각 팔레트 + (풀이 중) 지우기·확인, (채점 후) 결과 + 다음.
 */
@Composable
fun DissectionSolveBody(
    uiState: SolveUiState,
    callbacks: DissectionCallbacks,
    onNext: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val problem = uiState.problem ?: return
    val puzzle = problem.dissection ?: return
    val graded = uiState.phase == SolvePhase.GRADED
    Column(
        modifier = modifier.fillMaxWidth().padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        Text(
            text = problem.statement,
            style = MaterialTheme.typography.titleMedium,
            color = MaterialTheme.colorScheme.onSurface,
        )
        DissectionBoard(puzzle = puzzle, assignment = uiState.dissectionAssignment, onTap = callbacks.onTap)
        PiecePalette(puzzle.pieceCount, uiState.dissectionPiece, callbacks.onSelectPiece)

        if (!graded) {
            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                OutlinedButton(onClick = callbacks.onClear) { Text(stringResource(R.string.puzzle_clear)) }
                Button(onClick = callbacks.onSubmit) { Text(stringResource(R.string.puzzle_check)) }
            }
            // 미완성 힌트(풀이 중, 시도 기록 없음)
            uiState.dissectionResult?.takeIf { !it.isValid }?.let {
                Text(
                    text = dissectionHint(it.error),
                    color = MaterialTheme.colorScheme.error,
                    style = MaterialTheme.typography.bodyMedium,
                )
            }
        } else {
            val result = uiState.dissectionResult
            val (msg, color) =
                if (result?.isValid == true) {
                    stringResource(R.string.puzzle_correct) to MaterialTheme.colorScheme.secondary
                } else {
                    dissectionHint(result?.error) to MaterialTheme.colorScheme.error
                }
            Text(text = msg, color = color, fontWeight = FontWeight.Bold, style = MaterialTheme.typography.titleMedium)
            Button(onClick = onNext) { Text(stringResource(R.string.puzzle_next)) }
        }
    }
}
