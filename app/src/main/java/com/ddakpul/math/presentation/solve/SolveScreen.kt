package com.ddakpul.math.presentation.solve

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.LinearProgressIndicator
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
import com.ddakpul.math.core.designsystem.component.ChoiceOption
import com.ddakpul.math.core.designsystem.component.ChoiceState
import com.ddakpul.math.presentation.common.labelRes
import com.ddakpul.math.presentation.result.ResultView

@Composable
fun SolveScreen(
    modifier: Modifier = Modifier,
    viewModel: SolveViewModel = hiltViewModel(),
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    SolveContent(
        uiState = uiState,
        onSelect = viewModel::selectChoice,
        onSubmit = viewModel::submit,
        onNext = viewModel::loadNext,
        modifier = modifier,
    )
}

@Composable
private fun SolveContent(
    uiState: SolveUiState,
    onSelect: (Int) -> Unit,
    onSubmit: () -> Unit,
    onNext: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Box(modifier = modifier.fillMaxSize(), contentAlignment = Alignment.TopCenter) {
        when (uiState.phase) {
            SolvePhase.LOADING -> {
                CenterMessage { CircularProgressIndicator() }
            }

            SolvePhase.EMPTY -> {
                CenterMessage {
                    Text(stringResource(R.string.solve_empty), style = MaterialTheme.typography.bodyLarge)
                }
            }

            SolvePhase.SOLVING -> {
                // 태블릿에서 한 줄이 지나치게 길어지지 않도록 콘텐츠 폭을 제한한다.
                SolvingBody(uiState, onSelect, onSubmit, Modifier.widthIn(max = CONTENT_MAX_WIDTH))
            }

            SolvePhase.GRADED -> {
                uiState.result?.let { result ->
                    ResultView(
                        result = result,
                        showExplanation = uiState.showExplanation,
                        sessionStreak = uiState.sessionStreak,
                        onNext = onNext,
                        modifier = Modifier.widthIn(max = CONTENT_MAX_WIDTH),
                    )
                }
            }
        }
    }
}

@Composable
private fun SolvingBody(
    uiState: SolveUiState,
    onSelect: (Int) -> Unit,
    onSubmit: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val problem = uiState.problem ?: return
    Column(
        modifier = modifier.fillMaxWidth().verticalScroll(rememberScrollState()).padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        // 오늘의 목표 진행 — 근접 목표(proximal goal)가 유능감과 흥미를 만든다.
        TodayProgressHeader(todaySolved = uiState.todaySolved, dailyGoal = uiState.dailyGoal)

        uiState.area?.let { area ->
            Text(
                text = stringResource(R.string.solve_area_label, stringResource(area.labelRes()), uiState.difficulty),
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.primary,
                fontWeight = FontWeight.Bold,
            )
        }

        Card(
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceContainer),
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(
                text = problem.statement,
                style = MaterialTheme.typography.titleLarge,
                modifier = Modifier.fillMaxWidth().padding(24.dp),
            )
        }

        problem.choices.forEachIndexed { index, choice ->
            ChoiceOption(
                index = index,
                text = choice,
                state = if (uiState.selectedIndex == index) ChoiceState.SELECTED else ChoiceState.DEFAULT,
                onClick = { onSelect(index) },
                enabled = true,
            )
        }

        Button(
            onClick = onSubmit,
            enabled = uiState.canSubmit,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(
                text = stringResource(R.string.solve_submit),
                style = MaterialTheme.typography.titleMedium,
                modifier = Modifier.padding(vertical = 6.dp),
            )
        }
    }
}

@Composable
private fun TodayProgressHeader(
    todaySolved: Int,
    dailyGoal: Int,
) {
    Column(verticalArrangement = Arrangement.spacedBy(6.dp), modifier = Modifier.fillMaxWidth()) {
        Text(
            text = stringResource(R.string.solve_today_progress, todaySolved, dailyGoal),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        LinearProgressIndicator(
            progress = { (todaySolved.toFloat() / dailyGoal).coerceIn(0f, 1f) },
            modifier = Modifier.fillMaxWidth(),
        )
    }
}

@Composable
private fun CenterMessage(content: @Composable () -> Unit) {
    Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) { content() }
}

private val CONTENT_MAX_WIDTH = 640.dp
