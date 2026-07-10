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
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
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
import com.ddakpul.math.core.designsystem.component.StatTile
import com.ddakpul.math.domain.model.Difficulty
import com.ddakpul.math.domain.model.LearningStats
import com.ddakpul.math.domain.model.SessionGoals
import kotlin.math.roundToInt

@Composable
fun HomeScreen(
    onStartLearning: () -> Unit,
    modifier: Modifier = Modifier,
    viewModel: HomeViewModel = hiltViewModel(),
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    HomeContent(
        stats = uiState.stats,
        dailyGoal = uiState.dailyGoal,
        onStartLearning = onStartLearning,
        modifier = modifier,
    )
}

@Composable
private fun HomeContent(
    stats: LearningStats?,
    dailyGoal: Int,
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

        TodayGoalCard(
            todaySolved = stats?.todaySolved ?: 0,
            goal = dailyGoal,
            streakDays = stats?.streakDays ?: 0,
            bestStreakDays = stats?.bestStreakDays ?: 0,
            modifier = Modifier.fillMaxWidth().widthIn(max = 560.dp),
        )

        val solved = stats?.totalSolved ?: 0
        val accuracyPercent = ((stats?.accuracy ?: 0f) * 100).roundToInt()
        val level = stats?.currentDifficulty ?: Difficulty.DEFAULT
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

/**
 * 오늘의 목표 진행 + 연속 학습일. 근접 목표(Bandura & Schunk)와 관대한 스트릭
 * (어제까지 이어졌으면 유지) 설계 — 근거는 docs/PEDAGOGY.md.
 */
@Composable
private fun TodayGoalCard(
    todaySolved: Int,
    goal: Int,
    streakDays: Int,
    bestStreakDays: Int,
    modifier: Modifier = Modifier,
) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer),
    ) {
        Column(
            modifier = Modifier.fillMaxWidth().padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
            ) {
                Text(
                    text = stringResource(R.string.home_goal_title),
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onPrimaryContainer,
                )
                Text(
                    text =
                        if (todaySolved >= goal) {
                            stringResource(R.string.home_goal_done)
                        } else {
                            stringResource(R.string.home_goal_progress, todaySolved, goal)
                        },
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onPrimaryContainer,
                )
            }
            LinearProgressIndicator(
                progress = { (todaySolved.toFloat() / goal).coerceIn(0f, 1f) },
                modifier = Modifier.fillMaxWidth(),
            )
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
            ) {
                Text(
                    text =
                        if (streakDays > 0) {
                            stringResource(R.string.home_streak, streakDays)
                        } else {
                            stringResource(R.string.home_streak_start)
                        },
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onPrimaryContainer,
                )
                if (bestStreakDays > 1) {
                    Text(
                        text = stringResource(R.string.home_streak_best, bestStreakDays),
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onPrimaryContainer,
                    )
                }
            }
        }
    }
}
