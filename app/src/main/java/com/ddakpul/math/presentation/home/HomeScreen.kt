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
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
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
import com.ddakpul.math.core.designsystem.component.MasteryChip
import com.ddakpul.math.core.designsystem.component.ProgressBar
import com.ddakpul.math.core.designsystem.component.masteryStageOf
import com.ddakpul.math.domain.model.AreaStat
import com.ddakpul.math.domain.model.Difficulty
import com.ddakpul.math.domain.model.LearningStats
import com.ddakpul.math.domain.model.MathArea
import com.ddakpul.math.presentation.common.areaColor
import com.ddakpul.math.presentation.common.labelRes

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
        reviewDueCount = uiState.reviewDueCount,
        onStartLearning = onStartLearning,
        modifier = modifier,
    )
}

/**
 * 홈 리디자인(2026-07 시안) — 화면당 초점 하나: 오늘의 목표 히어로 카드가 주인공이고,
 * 통계 타일 대신 실력 지도 한 카드로 모은다. CTA는 다음 학습을 이어가는 단 하나의 행동.
 */
@Composable
private fun HomeContent(
    stats: LearningStats?,
    dailyGoal: Int,
    reviewDueCount: Int,
    onStartLearning: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Column(
        // 태블릿(>560dp)에서 폭 제한된 카드들이 왼쪽으로 쏠리지 않도록 가운데 정렬
        // (문제풀이 화면 Box(TopCenter)와 동일). 폰(<560dp)에선 카드가 전체 폭이라 영향 없음.
        modifier = modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        HomeHeader(
            streakDays = stats?.streakDays ?: 0,
            modifier = Modifier.widthIn(max = CONTENT_MAX_WIDTH).fillMaxWidth(),
        )

        TodayGoalHeroCard(
            todaySolved = stats?.todaySolved ?: 0,
            goal = dailyGoal,
            modifier = Modifier.widthIn(max = CONTENT_MAX_WIDTH).fillMaxWidth(),
        )

        StartLearningCta(
            hasHistory = stats?.isEmpty == false,
            difficulty = stats?.currentDifficulty ?: Difficulty.DEFAULT,
            onClick = onStartLearning,
            modifier = Modifier.widthIn(max = CONTENT_MAX_WIDTH).fillMaxWidth(),
        )

        if (reviewDueCount > 0) {
            ReviewReadyCard(
                count = reviewDueCount,
                onClick = onStartLearning,
                modifier = Modifier.widthIn(max = CONTENT_MAX_WIDTH).fillMaxWidth(),
            )
        }

        SkillMapCard(
            stats = stats,
            modifier = Modifier.widthIn(max = CONTENT_MAX_WIDTH).fillMaxWidth(),
        )
    }
}

/** 타이틀·인사(왼쪽) + 스트릭 필(오른쪽). 스트릭이 없으면 필을 숨긴다. */
@Composable
private fun HomeHeader(
    streakDays: Int,
    modifier: Modifier = Modifier,
) {
    Row(modifier = modifier, verticalAlignment = Alignment.CenterVertically) {
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
        if (streakDays > 0) {
            Surface(
                color = MaterialTheme.colorScheme.tertiaryContainer,
                contentColor = MaterialTheme.colorScheme.onTertiaryContainer,
                shape = CircleShape,
            ) {
                Text(
                    text = stringResource(R.string.home_streak_pill, streakDays),
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.padding(horizontal = 14.dp, vertical = 8.dp),
                )
            }
        }
    }
}

/**
 * 오늘의 목표 히어로 — 큰 숫자 + 도넛 링 + 목표 칸 점 진행.
 * 근접 목표(Bandura & Schunk)가 유능감을 만든다(docs/PEDAGOGY.md). 셀 수 있는 진행 칸이 힘을 준다.
 */
@Composable
private fun TodayGoalHeroCard(
    todaySolved: Int,
    goal: Int,
    modifier: Modifier = Modifier,
) {
    Card(
        modifier = modifier,
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceContainer),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp),
    ) {
        Column(
            modifier = Modifier.fillMaxWidth().padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Column(
                    modifier = Modifier.weight(1f),
                    verticalArrangement = Arrangement.spacedBy(6.dp),
                ) {
                    Text(
                        text = stringResource(R.string.home_goal_title),
                        style = MaterialTheme.typography.titleMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                    Row(verticalAlignment = Alignment.Bottom) {
                        Text(
                            text = todaySolved.toString(),
                            style = MaterialTheme.typography.displaySmall,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.onSurface,
                        )
                        Text(
                            text = stringResource(R.string.home_goal_of, goal),
                            style = MaterialTheme.typography.titleMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                            modifier = Modifier.padding(start = 4.dp, bottom = 4.dp),
                        )
                    }
                    Text(
                        text =
                            if (todaySolved >= goal) {
                                stringResource(R.string.home_goal_done)
                            } else {
                                stringResource(R.string.home_goal_remaining, goal - todaySolved)
                            },
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
                Spacer(Modifier.width(16.dp))
                GoalRing(solved = todaySolved, goal = goal)
            }
            GoalSegments(solved = todaySolved, goal = goal)
        }
    }
}

/** 목표 칸 점 진행 — 목표 수만큼 칸을 놓고 푼 만큼 채운다(셀 수 있는 근접 목표). */
@Composable
private fun GoalSegments(
    solved: Int,
    goal: Int,
    modifier: Modifier = Modifier,
) {
    Row(modifier = modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(5.dp)) {
        repeat(goal) { index ->
            val filled = index < solved
            Box(
                modifier =
                    Modifier
                        .weight(1f)
                        .height(8.dp)
                        .clip(RoundedCornerShape(4.dp))
                        .background(
                            if (filled) {
                                MaterialTheme.colorScheme.secondary
                            } else {
                                MaterialTheme.colorScheme.outlineVariant
                            },
                        ),
            )
        }
    }
}

/** 오늘 목표 진행 도넛 링 — 트랙 위 민트 진행 호, 중앙에 달성률 %. */
@Composable
private fun GoalRing(
    solved: Int,
    goal: Int,
    modifier: Modifier = Modifier,
) {
    val progress = if (goal > 0) (solved.toFloat() / goal).coerceIn(0f, 1f) else 0f
    val trackColor = MaterialTheme.colorScheme.surfaceContainerHigh
    val arcColor = MaterialTheme.colorScheme.secondary
    Box(modifier = modifier.size(88.dp), contentAlignment = Alignment.Center) {
        Canvas(modifier = Modifier.fillMaxSize()) {
            val stroke = 10.dp.toPx()
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
        Text(
            text = stringResource(R.string.home_unit_percent, progress.toPercentInt()),
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onSecondaryContainer,
        )
    }
}

/**
 * 학습 CTA — "이어서 풀기" + 난이도 서브라인으로 다음에 무엇이 나올지 미리 알린다
 * (추천 알고리즘이 하는 일을 처음으로 눈에 보이게). 기록이 없으면 "학습 시작".
 */
@Composable
private fun StartLearningCta(
    hasHistory: Boolean,
    difficulty: Int,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    GradientPrimaryButton(onClick = onClick, modifier = modifier) {
        Row(
            modifier = Modifier.weight(1f),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            Box(
                modifier =
                    Modifier
                        .size(44.dp)
                        .background(playHaloColor(), CircleShape),
                contentAlignment = Alignment.Center,
            ) {
                Icon(imageVector = Icons.Filled.PlayArrow, contentDescription = null)
            }
            Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                Text(
                    text = stringResource(if (hasHistory) R.string.home_cta_continue else R.string.home_start),
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold,
                )
                Text(
                    text = stringResource(R.string.home_cta_level, difficulty),
                    style = MaterialTheme.typography.labelLarge,
                )
            }
        }
    }
}

/** CTA 아이콘 뒤 반투명 원 — onPrimary에서 파생해 라이트/다크 모두 자연스럽다. */
@Composable
private fun playHaloColor() = MaterialTheme.colorScheme.onPrimary.copy(alpha = PLAY_HALO_ALPHA)

/** 복습 만기 안내 카드 — 규칙 8(Leitner 간격 복습)을 처음으로 화면에 드러낸다. */
@Composable
private fun ReviewReadyCard(
    count: Int,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Surface(
        onClick = onClick,
        modifier = modifier,
        color = MaterialTheme.colorScheme.tertiaryContainer,
        contentColor = MaterialTheme.colorScheme.onTertiaryContainer,
        shape = RoundedCornerShape(20.dp),
    ) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(16.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Text(text = "🔁", style = MaterialTheme.typography.titleMedium)
            Text(
                text = stringResource(R.string.home_review_ready, count),
                style = MaterialTheme.typography.bodyLarge,
                modifier = Modifier.weight(1f),
            )
            Text(
                text = stringResource(R.string.home_review_go),
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.Bold,
            )
        }
    }
}

/** 내 실력 지도 — 흩어져 있던 통계를 4영역 진행바 + 숙달 칩 한 카드로 모은다. */
@Composable
private fun SkillMapCard(
    stats: LearningStats?,
    modifier: Modifier = Modifier,
) {
    val byArea = stats?.areaStats.orEmpty().associateBy { it.area }
    Card(
        modifier = modifier,
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceContainer),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp),
    ) {
        Column(
            modifier = Modifier.fillMaxWidth().padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = stringResource(R.string.home_skill_title),
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onSurface,
                    modifier = Modifier.weight(1f),
                )
                Text(
                    text =
                        stringResource(
                            R.string.home_skill_summary,
                            stats?.totalSolved ?: 0,
                            (stats?.accuracy ?: 0f).toPercentInt(),
                        ),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            MathArea.entries.forEach { area ->
                val stat = byArea[area] ?: AreaStat(area = area, solved = 0, correct = 0)
                SkillMapRow(stat = stat)
            }
        }
    }
}

@Composable
private fun SkillMapRow(
    stat: AreaStat,
    modifier: Modifier = Modifier,
) {
    Column(modifier = modifier.fillMaxWidth(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Box(modifier = Modifier.size(8.dp).background(stat.area.areaColor(), CircleShape))
            Text(
                text = stringResource(stat.area.labelRes()),
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.onSurface,
                modifier = Modifier.weight(1f),
            )
            MasteryChip(stage = masteryStageOf(solved = stat.solved, accuracy = stat.accuracy))
        }
        ProgressBar(
            fraction = stat.accuracy,
            color = stat.area.areaColor(),
            trackColor = MaterialTheme.colorScheme.surfaceContainerHigh,
            height = 8.dp,
            modifier = Modifier.fillMaxWidth(),
        )
    }
}

private val CONTENT_MAX_WIDTH = 560.dp
private const val PLAY_HALO_ALPHA = 0.18f
