package com.ddakpul.math.presentation.puzzle

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
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
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.ddakpul.math.R

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

        DissectionBoard(puzzle = state.pilot.puzzle, assignment = state.assignment, onTap = viewModel::tapCell)
        PiecePalette(state.pilot.puzzle.pieceCount, state.selectedPiece, viewModel::selectPiece)

        Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            OutlinedButton(onClick = viewModel::clear) { Text(stringResource(R.string.puzzle_clear)) }
            Button(onClick = viewModel::check) { Text(stringResource(R.string.puzzle_check)) }
        }

        state.result?.let { result ->
            val (msg, color) =
                if (result.isValid) {
                    stringResource(R.string.puzzle_correct) to MaterialTheme.colorScheme.secondary
                } else {
                    dissectionHint(result.error) to MaterialTheme.colorScheme.error
                }
            Text(text = msg, color = color, fontWeight = FontWeight.Bold, style = MaterialTheme.typography.titleMedium)
            if (result.isValid) {
                Button(onClick = viewModel::next) { Text(stringResource(R.string.puzzle_next)) }
            }
        }
    }
}
