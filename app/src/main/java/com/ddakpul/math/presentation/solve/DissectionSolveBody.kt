package com.ddakpul.math.presentation.solve

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.ddakpul.math.R
import com.ddakpul.math.presentation.puzzle.DissectionBoard
import com.ddakpul.math.presentation.puzzle.DissectionControls
import com.ddakpul.math.presentation.puzzle.DissectionResultText
import com.ddakpul.math.presentation.puzzle.PiecePalette
import com.ddakpul.math.presentation.puzzle.dissectionHint

/**
 * 본 풀이 흐름 안의 등분 퍼즐 화면 — 4지선다 [SolvingBody]/[ResultSheet]에 대응하는 구성형 경로.
 * 격자 탭 입력판 + 조각 팔레트 + (풀이 중) 지우기·확인, (채점 후) 결과 + 다음.
 *
 * 4지선다와 같은 머리(진행 점 + ⋯ 메뉴, 영역·난이도 칩)를 공유한다 — 진행 상황을 볼 수 없고
 * 문제를 바꿀 방법도 없어, 못 푸는 퍼즐을 만나면 앱을 재시작해야 벗어나던 문제를 없앤다(2026-08 QA).
 */
@Composable
fun DissectionSolveBody(
    uiState: SolveUiState,
    callbacks: DissectionCallbacks,
    onNext: () -> Unit,
    modifier: Modifier = Modifier,
    reviewMode: Boolean = false,
    onExcludeRequest: () -> Unit = {},
) {
    val problem = uiState.problem ?: return
    val puzzle = problem.dissection ?: return
    val graded = uiState.phase == SolvePhase.GRADED
    Column(modifier = modifier.fillMaxWidth().fillMaxHeight()) {
        SolveProgressRow(
            uiState = uiState,
            reviewMode = reviewMode,
            engineLabel = "",
            onExcludeRequest = onExcludeRequest,
        )
        SolveMetaRow(uiState = uiState, reviewMode = reviewMode)
        Column(
            modifier =
                Modifier
                    .weight(1f)
                    .verticalScroll(rememberScrollState())
                    .padding(horizontal = 16.dp, vertical = 12.dp),
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
                DissectionControls(onClear = callbacks.onClear, onCheck = callbacks.onSubmit)
                // 미완성 힌트(풀이 중, 시도 기록 없음)
                uiState.dissectionResult?.takeIf { !it.isValid }?.let {
                    Text(
                        text = dissectionHint(it.error),
                        color = MaterialTheme.colorScheme.error,
                        style = MaterialTheme.typography.bodyMedium,
                    )
                }
            } else {
                DissectionResultText(uiState.dissectionResult)
                Button(onClick = onNext) {
                    Text(stringResource(if (reviewMode) R.string.review_back else R.string.puzzle_next))
                }
            }
        }
    }
}
