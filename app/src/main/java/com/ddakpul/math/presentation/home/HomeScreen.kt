package com.ddakpul.math.presentation.home

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.ddakpul.math.R
import com.ddakpul.math.core.common.toPercentInt
import com.ddakpul.math.core.designsystem.component.GradientPrimaryButton
import com.ddakpul.math.core.designsystem.component.StatTile
import com.ddakpul.math.domain.model.Difficulty
import com.ddakpul.math.domain.model.LearningStats
import com.ddakpul.math.presentation.common.launchFreeDeadlineText
import kotlin.math.roundToInt

@Composable
fun HomeScreen(
    onStartLearning: () -> Unit,
    onOpenPuzzle: () -> Unit,
    modifier: Modifier = Modifier,
    viewModel: HomeViewModel = hiltViewModel(),
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    HomeContent(
        stats = uiState.stats,
        dailyGoal = uiState.dailyGoal,
        launchFreeUntilMillis = uiState.launchFreeUntilMillis,
        onStartLearning = onStartLearning,
        onOpenPuzzle = onOpenPuzzle,
        modifier = modifier,
    )
}

@Composable
private fun HomeContent(
    stats: LearningStats?,
    dailyGoal: Int,
    launchFreeUntilMillis: Long,
    onStartLearning: () -> Unit,
    onOpenPuzzle: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Column(
        // 태블릿(>560dp)에서 폭 제한된 카드들이 왼쪽으로 쏠리지 않도록 가운데 정렬
        // (문제풀이 화면 Box(TopCenter)와 동일). 폰(<560dp)에선 카드가 전체 폭이라 영향 없음.
        modifier = modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(20.dp),
    ) {
        // 헤더: 타이틀·인사(왼쪽) + 마스코트(오른쪽). 마스코트는 임시 스마일(실제 딱풀이는 출시 후).
        Row(
            modifier = Modifier.widthIn(max = 560.dp).fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = stringResource(R.string.app_name),
                    style = MaterialTheme.typography.headlineMedium,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onSurface,
                )
                Spacer(Modifier.height(4.dp))
                Text(
                    text = stringResource(R.string.home_greeting),
                    style = MaterialTheme.typography.bodyLarge,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            MascotPlaceholder()
        }

        if (launchFreeUntilMillis > 0L) {
            LaunchFreeBanner(
                untilMillis = launchFreeUntilMillis,
                modifier = Modifier.widthIn(max = 560.dp).fillMaxWidth(),
            )
        }

        TodayGoalCard(
            todaySolved = stats?.todaySolved ?: 0,
            goal = dailyGoal,
            streakDays = stats?.streakDays ?: 0,
            bestStreakDays = stats?.bestStreakDays ?: 0,
            modifier = Modifier.widthIn(max = 560.dp).fillMaxWidth(),
        )

        val solved = stats?.totalSolved ?: 0
        val accuracyPercent = (stats?.accuracy ?: 0f).toPercentInt()
        val level = stats?.currentDifficulty ?: Difficulty.DEFAULT
        val tileColor = MaterialTheme.colorScheme.surfaceContainerHigh
        Row(
            modifier = Modifier.widthIn(max = 560.dp).fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            StatTile(
                icon = "📚",
                label = stringResource(R.string.home_stat_solved),
                value = stringResource(R.string.home_unit_count, solved),
                containerColor = tileColor,
                modifier = Modifier.weight(1f),
            )
            StatTile(
                icon = "🎯",
                label = stringResource(R.string.home_stat_accuracy),
                value = stringResource(R.string.home_unit_percent, accuracyPercent),
                containerColor = tileColor,
                modifier = Modifier.weight(1f),
            )
            StatTile(
                icon = "🏆",
                label = stringResource(R.string.home_stat_difficulty),
                value = stringResource(R.string.home_unit_level, level),
                containerColor = tileColor,
                modifier = Modifier.weight(1f),
            )
        }

        GradientPrimaryButton(
            onClick = onStartLearning,
            modifier = Modifier.widthIn(max = 560.dp).fillMaxWidth(),
        ) {
            Icon(imageVector = Icons.Filled.PlayArrow, contentDescription = null)
            Text(
                text = stringResource(R.string.home_start),
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.padding(start = 8.dp),
            )
        }

        PuzzleEntryCard(
            onClick = onOpenPuzzle,
            modifier = Modifier.widthIn(max = 560.dp).fillMaxWidth(),
        )
    }
}

/** 공간 퍼즐 미리보기 진입 카드 — 새 모달리티(격자 등분) 파일럿. */
@Composable
private fun PuzzleEntryCard(
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Card(
        onClick = onClick,
        modifier = modifier,
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceContainerHigh),
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(4.dp),
        ) {
            Text(
                text = stringResource(R.string.puzzle_home_card),
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onSurface,
            )
            Text(
                text = stringResource(R.string.puzzle_home_card_desc),
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

/** 출시 기념 무료 안내 배너 — 압박 없이 정직하게 마감일과 이후 정책을 알린다. */
@Composable
private fun LaunchFreeBanner(
    untilMillis: Long,
    modifier: Modifier = Modifier,
) {
    Card(
        modifier = modifier,
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.tertiaryContainer),
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(4.dp),
        ) {
            Text(
                text = stringResource(R.string.home_launch_free_title, launchFreeDeadlineText(untilMillis)),
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onTertiaryContainer,
            )
            Text(
                text = stringResource(R.string.home_launch_free_desc),
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onTertiaryContainer,
            )
        }
    }
}

/**
 * 오늘의 목표 진행 + 연속 학습일. 근접 목표(Bandura & Schunk)와 관대한 스트릭
 * (어제까지 이어졌으면 유지) 설계 — 근거는 docs/PEDAGOGY.md.
 * 목업대로 흰 카드 + 오른쪽 도넛 링(오늘 푼 수/목표).
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
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceContainer),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp),
    ) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(20.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Column(
                modifier = Modifier.weight(1f),
                verticalArrangement = Arrangement.spacedBy(6.dp),
            ) {
                Text(
                    text = stringResource(R.string.home_goal_title),
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onSurface,
                )
                Text(
                    text =
                        if (streakDays > 0) {
                            stringResource(R.string.home_streak, streakDays)
                        } else {
                            stringResource(R.string.home_streak_start)
                        },
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                if (bestStreakDays > 1) {
                    Text(
                        text = stringResource(R.string.home_streak_best, bestStreakDays),
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
            }
            Spacer(Modifier.width(16.dp))
            GoalRing(solved = todaySolved, goal = goal)
        }
    }
}

/** 오늘 목표 진행 도넛 링 — 회색 트랙 위에 민트 진행 호, 중앙에 오늘 푼 수/목표. */
@Composable
private fun GoalRing(
    solved: Int,
    goal: Int,
    modifier: Modifier = Modifier,
) {
    val progress = if (goal > 0) (solved.toFloat() / goal).coerceIn(0f, 1f) else 0f
    val trackColor = MaterialTheme.colorScheme.outlineVariant
    val arcColor = MaterialTheme.colorScheme.secondary
    Box(modifier = modifier.size(64.dp), contentAlignment = Alignment.Center) {
        Canvas(modifier = Modifier.fillMaxSize()) {
            val stroke = 7.dp.toPx()
            val inset = stroke / 2f
            val arcSize = Size(size.width - stroke, size.height - stroke)
            drawArc(
                color = trackColor,
                startAngle = 0f,
                sweepAngle = 360f,
                useCenter = false,
                topLeft = Offset(inset, inset),
                size = arcSize,
                style = Stroke(width = stroke),
            )
            if (progress > 0f) {
                drawArc(
                    color = arcColor,
                    startAngle = -90f,
                    sweepAngle = 360f * progress,
                    useCenter = false,
                    topLeft = Offset(inset, inset),
                    size = arcSize,
                    style = Stroke(width = stroke, cap = StrokeCap.Round),
                )
            }
        }
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Text(
                text = solved.toString(),
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onSurface,
            )
            Text(
                text = "/$goal",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

/** 임시 마스코트 — 노란 스마일. 실제 '딱풀이'는 출시 후 교체 예정. */
@Composable
private fun MascotPlaceholder(modifier: Modifier = Modifier) {
    val halo = MaterialTheme.colorScheme.primaryContainer
    Box(
        modifier = modifier.size(64.dp).background(halo, CircleShape),
        contentAlignment = Alignment.Center,
    ) {
        Canvas(modifier = Modifier.size(44.dp)) {
            val face = Color(0xFFFFD54F)
            val ink = Color(0xFF3A2E00)
            val r = size.minDimension / 2f
            drawCircle(color = face, radius = r)
            val eyeR = r * 0.11f
            val eyeY = center.y - r * 0.14f
            drawCircle(color = ink, radius = eyeR, center = Offset(center.x - r * 0.36f, eyeY))
            drawCircle(color = ink, radius = eyeR, center = Offset(center.x + r * 0.36f, eyeY))
            val smileW = r * 1.05f
            val smileH = r * 0.85f
            drawArc(
                color = ink,
                startAngle = 20f,
                sweepAngle = 140f,
                useCenter = false,
                topLeft = Offset(center.x - smileW / 2f, center.y - smileH * 0.10f),
                size = Size(smileW, smileH),
                style = Stroke(width = r * 0.13f, cap = StrokeCap.Round),
            )
        }
    }
}
