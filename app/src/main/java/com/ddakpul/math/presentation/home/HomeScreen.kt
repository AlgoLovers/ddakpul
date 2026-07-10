package com.ddakpul.math.presentation.home

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material3.Button
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
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
import com.ddakpul.math.core.designsystem.component.StatTile
import com.ddakpul.math.domain.model.Difficulty
import com.ddakpul.math.domain.model.LearnerReport
import kotlin.math.roundToInt

@Composable
fun HomeScreen(
    onStartLearning: () -> Unit,
    modifier: Modifier = Modifier,
    viewModel: HomeViewModel = hiltViewModel(),
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    HomeContent(report = uiState.report, onStartLearning = onStartLearning, modifier = modifier)
}

@Composable
private fun HomeContent(
    report: LearnerReport?,
    onStartLearning: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Column(
        modifier = modifier.fillMaxSize().padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(24.dp),
    ) {
        Text(
            text = stringResource(R.string.app_name),
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.primary,
        )
        Text(
            text = stringResource(R.string.home_greeting),
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )

        val solved = report?.totalSolved ?: 0
        val accuracyPercent = ((report?.accuracy ?: 0f) * 100).roundToInt()
        val level = report?.currentDifficulty ?: Difficulty.DEFAULT
        Row(
            modifier = Modifier.fillMaxWidth().widthIn(max = 560.dp),
            horizontalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            StatTile(
                label = stringResource(R.string.home_stat_solved),
                value = stringResource(R.string.home_unit_count, solved),
                modifier = Modifier.weight(1f),
            )
            StatTile(
                label = stringResource(R.string.home_stat_accuracy),
                value = stringResource(R.string.home_unit_percent, accuracyPercent),
                modifier = Modifier.weight(1f),
            )
            StatTile(
                label = stringResource(R.string.home_stat_difficulty),
                value = stringResource(R.string.home_unit_level, level),
                modifier = Modifier.weight(1f),
            )
        }

        Button(
            onClick = onStartLearning,
            modifier = Modifier.fillMaxWidth().widthIn(max = 400.dp),
        ) {
            Icon(imageVector = Icons.Filled.PlayArrow, contentDescription = null)
            Text(
                text = stringResource(R.string.home_start),
                style = MaterialTheme.typography.titleMedium,
                modifier = Modifier.padding(vertical = 8.dp, horizontal = 8.dp),
            )
        }
    }
}
