package com.ddakpul.math.presentation.onboarding

import androidx.compose.foundation.background
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
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.ddakpul.math.R
import com.ddakpul.math.domain.model.Difficulty
import com.ddakpul.math.domain.model.SessionGoals

/** 하루 목표 선택지(설정 화면과 동일). */
private val GOAL_OPTIONS = listOf(5, 10, 15)
private const val STEP_COUNT = 3

// 온보딩 시작 난이도 선택지 → 실제 난이도 값
private const val LEVEL_EASY = Difficulty.MIN
private const val LEVEL_MID = Difficulty.DEFAULT
private const val LEVEL_HARD = 3

/**
 * 첫 실행 온보딩 — 앱 소개 → 하루 목표 → 시작 난이도의 3단계.
 * [onComplete]에 (시작 난이도, 하루 목표)를 넘기면 본화면으로 넘어간다.
 */
@Composable
fun OnboardingScreen(
    onComplete: (startingDifficulty: Int, dailyGoal: Int) -> Unit,
    modifier: Modifier = Modifier,
) {
    var step by remember { mutableIntStateOf(0) }
    var dailyGoal by remember { mutableIntStateOf(SessionGoals.DAILY_GOAL_PROBLEMS) }
    var startingDifficulty by remember { mutableIntStateOf(Difficulty.DEFAULT) }

    Column(
        modifier = modifier.fillMaxSize().padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        StepDots(current = step, total = STEP_COUNT)
        Column(
            modifier =
                Modifier
                    .weight(1f)
                    .fillMaxWidth()
                    .widthIn(max = CONTENT_MAX_WIDTH)
                    .verticalScroll(rememberScrollState())
                    .padding(vertical = 24.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            when (step) {
                0 -> IntroStep()
                1 -> GoalStep(selected = dailyGoal, onSelect = { dailyGoal = it })
                else -> LevelStep(selected = startingDifficulty, onSelect = { startingDifficulty = it })
            }
        }
        Row(
            modifier = Modifier.fillMaxWidth().widthIn(max = CONTENT_MAX_WIDTH),
            horizontalArrangement = Arrangement.spacedBy(12.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            if (step > 0) {
                OutlinedButton(onClick = { step -= 1 }) {
                    Text(stringResource(R.string.onboarding_back))
                }
            }
            Button(
                onClick = {
                    if (step < STEP_COUNT - 1) {
                        step += 1
                    } else {
                        onComplete(startingDifficulty, dailyGoal)
                    }
                },
                modifier = Modifier.weight(1f),
            ) {
                Text(
                    text = stringResource(if (step < STEP_COUNT - 1) R.string.onboarding_next else R.string.onboarding_start),
                    style = MaterialTheme.typography.titleMedium,
                    modifier = Modifier.padding(vertical = 6.dp),
                )
            }
        }
    }
}

@Composable
private fun IntroStep() {
    Text(
        text = stringResource(R.string.onboarding_welcome_title),
        style = MaterialTheme.typography.headlineSmall,
        fontWeight = FontWeight.Bold,
    )
    Text(
        text = stringResource(R.string.onboarding_welcome_subtitle),
        style = MaterialTheme.typography.bodyLarge,
        color = MaterialTheme.colorScheme.onSurfaceVariant,
    )
    Spacer(Modifier.size(8.dp))
    ValueRow("🧩", R.string.onboarding_value1_title, R.string.onboarding_value1_body)
    ValueRow("🛡️", R.string.onboarding_value2_title, R.string.onboarding_value2_body)
    ValueRow("🌱", R.string.onboarding_value3_title, R.string.onboarding_value3_body)
}

@Composable
private fun ValueRow(
    emoji: String,
    titleRes: Int,
    bodyRes: Int,
) {
    Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
        Text(text = emoji, style = MaterialTheme.typography.headlineSmall)
        Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
            Text(
                text = stringResource(titleRes),
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
            )
            Text(
                text = stringResource(bodyRes),
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

@Composable
private fun GoalStep(
    selected: Int,
    onSelect: (Int) -> Unit,
) {
    StepHeader(R.string.onboarding_goal_title, R.string.onboarding_goal_subtitle)
    Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
        GOAL_OPTIONS.forEach { goal ->
            FilterChip(
                selected = selected == goal,
                onClick = { onSelect(goal) },
                label = { Text(stringResource(R.string.onboarding_goal_chip, goal)) },
            )
        }
    }
}

@Composable
private fun LevelStep(
    selected: Int,
    onSelect: (Int) -> Unit,
) {
    StepHeader(R.string.onboarding_level_title, R.string.onboarding_level_subtitle)
    SelectableOption(
        selected = selected == LEVEL_EASY,
        onClick = { onSelect(LEVEL_EASY) },
        titleRes = R.string.onboarding_level_easy_title,
        bodyRes = R.string.onboarding_level_easy_body,
    )
    SelectableOption(
        selected = selected == LEVEL_MID,
        onClick = { onSelect(LEVEL_MID) },
        titleRes = R.string.onboarding_level_mid_title,
        bodyRes = R.string.onboarding_level_mid_body,
    )
    SelectableOption(
        selected = selected == LEVEL_HARD,
        onClick = { onSelect(LEVEL_HARD) },
        titleRes = R.string.onboarding_level_hard_title,
        bodyRes = R.string.onboarding_level_hard_body,
    )
}

@Composable
private fun StepHeader(
    titleRes: Int,
    subtitleRes: Int,
) {
    Text(
        text = stringResource(titleRes),
        style = MaterialTheme.typography.headlineSmall,
        fontWeight = FontWeight.Bold,
    )
    Text(
        text = stringResource(subtitleRes),
        style = MaterialTheme.typography.bodyMedium,
        color = MaterialTheme.colorScheme.onSurfaceVariant,
    )
}

@Composable
private fun SelectableOption(
    selected: Boolean,
    onClick: () -> Unit,
    titleRes: Int,
    bodyRes: Int,
) {
    val colors = MaterialTheme.colorScheme
    Card(
        colors =
            CardDefaults.cardColors(
                containerColor = if (selected) colors.secondaryContainer else colors.surfaceVariant,
                contentColor = if (selected) colors.onSecondaryContainer else colors.onSurfaceVariant,
            ),
        modifier = Modifier.fillMaxWidth().clickable(onClick = onClick),
    ) {
        Column(
            modifier = Modifier.fillMaxWidth().padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(4.dp),
        ) {
            Text(
                text = stringResource(titleRes),
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
            )
            Text(text = stringResource(bodyRes), style = MaterialTheme.typography.bodyMedium)
        }
    }
}

@Composable
private fun StepDots(
    current: Int,
    total: Int,
) {
    val colors = MaterialTheme.colorScheme
    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        repeat(total) { index ->
            Box(
                modifier =
                    Modifier
                        .size(if (index == current) 10.dp else 8.dp)
                        .clip(CircleShape)
                        .background(if (index == current) colors.primary else colors.surfaceVariant),
            )
        }
    }
}

private val CONTENT_MAX_WIDTH = 480.dp
