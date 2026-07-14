package com.ddakpul.math.presentation.settings

import android.content.Intent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.ddakpul.math.R
import com.ddakpul.math.domain.model.SessionGoals
import com.ddakpul.math.presentation.common.launchFreeDeadlineText

@Composable
fun SettingsScreen(
    onOpenPaywall: () -> Unit,
    onOpenPrivacy: () -> Unit,
    modifier: Modifier = Modifier,
    viewModel: SettingsViewModel = hiltViewModel(),
) {
    var showResetDialog by remember { mutableStateOf(false) }
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val pendingShareText by viewModel.pendingShareText.collectAsStateWithLifecycle()

    // 내보내기 텍스트가 준비되면 공유 시트를 띄운다(텔레그램 등 아무 앱으로나 전달 가능).
    val context = LocalContext.current
    LaunchedEffect(pendingShareText) {
        val text = pendingShareText ?: return@LaunchedEffect
        val sendIntent =
            Intent(Intent.ACTION_SEND).apply {
                type = "text/plain"
                putExtra(Intent.EXTRA_TEXT, text)
            }
        context.startActivity(Intent.createChooser(sendIntent, null))
        viewModel.consumeShareText()
    }

    Column(
        modifier = modifier.fillMaxSize().padding(24.dp),
        verticalArrangement = Arrangement.spacedBy(20.dp),
    ) {
        Text(
            text = stringResource(R.string.settings_title),
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
        )

        // 이용권 — 난이도 4~7과 전체 리포트를 여는 진입점. 현재 상태(무료/이용중)도 보여준다.
        PremiumCard(
            isPremium = uiState.isPremium,
            daysLeft = uiState.premiumDaysLeft,
            launchFreeUntilMillis = uiState.launchFreeUntilMillis,
            onOpenPaywall = onOpenPaywall,
        )

        // 하루 목표 — 아이가 스스로 정한다(자율성, SDT).
        DailyGoalCard(dailyGoal = uiState.dailyGoal, onSelect = viewModel::setDailyGoal)

        // 별로였던 문제 내보내기 — 부모가 개발 채널로 보내면 다음 업데이트에 반영된다.
        FeedbackExportCard(
            excludedCount = uiState.excludedCount,
            onShare = viewModel::requestExclusionShare,
        )

        ResetCard(onResetRequest = { showResetDialog = true })

        // 개인정보·데이터 안전 — 스토어 요건이자 신뢰 메시지.
        PrivacyCard(onOpenPrivacy = onOpenPrivacy)

        Text(
            text = stringResource(R.string.settings_about),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }

    if (showResetDialog) {
        ResetConfirmDialog(
            onConfirm = {
                viewModel.resetProgress()
                showResetDialog = false
            },
            onDismiss = { showResetDialog = false },
        )
    }
}

@Composable
private fun PremiumCard(
    isPremium: Boolean,
    daysLeft: Int,
    launchFreeUntilMillis: Long,
    onOpenPaywall: () -> Unit,
) {
    val launchFree = !isPremium && launchFreeUntilMillis > 0L
    SettingsCard {
        Text(
            text = stringResource(R.string.settings_premium_title),
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
        )
        Text(
            text =
                when {
                    isPremium -> stringResource(R.string.settings_premium_active, daysLeft)
                    launchFree -> stringResource(R.string.settings_launch_free, launchFreeDeadlineText(launchFreeUntilMillis))
                    else -> stringResource(R.string.settings_premium_desc)
                },
            style = MaterialTheme.typography.bodyMedium,
            color =
                when {
                    isPremium -> MaterialTheme.colorScheme.primary
                    launchFree -> MaterialTheme.colorScheme.tertiary
                    else -> MaterialTheme.colorScheme.onSurfaceVariant
                },
        )
        OutlinedButton(onClick = onOpenPaywall) {
            Text(stringResource(if (isPremium) R.string.settings_premium_manage else R.string.settings_premium_open))
        }
    }
}

@Composable
private fun PrivacyCard(onOpenPrivacy: () -> Unit) {
    SettingsCard {
        Text(
            text = stringResource(R.string.settings_privacy_title),
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
        )
        Text(
            text = stringResource(R.string.settings_privacy_desc),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        OutlinedButton(onClick = onOpenPrivacy) {
            Text(stringResource(R.string.settings_privacy_open))
        }
    }
}

@Composable
private fun DailyGoalCard(
    dailyGoal: Int,
    onSelect: (Int) -> Unit,
) {
    SettingsCard {
        Text(
            text = stringResource(R.string.settings_goal_title),
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
        )
        Text(
            text = stringResource(R.string.settings_goal_desc),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            SessionGoals.GOAL_OPTIONS.forEach { option ->
                FilterChip(
                    selected = dailyGoal == option,
                    onClick = { onSelect(option) },
                    label = { Text(stringResource(R.string.settings_goal_option, option)) },
                )
            }
        }
    }
}

@Composable
private fun FeedbackExportCard(
    excludedCount: Int,
    onShare: () -> Unit,
) {
    SettingsCard {
        Text(
            text = stringResource(R.string.settings_feedback_title),
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
        )
        Text(
            text = stringResource(R.string.settings_feedback_desc),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        if (excludedCount > 0) {
            OutlinedButton(onClick = onShare) {
                Text(stringResource(R.string.settings_feedback_share, excludedCount))
            }
        } else {
            Text(
                text = stringResource(R.string.settings_feedback_empty),
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

@Composable
private fun ResetCard(onResetRequest: () -> Unit) {
    SettingsCard {
        Text(
            text = stringResource(R.string.settings_reset),
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
        )
        Text(
            text = stringResource(R.string.settings_reset_desc),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        OutlinedButton(onClick = onResetRequest) {
            Text(stringResource(R.string.settings_reset_confirm))
        }
    }
}

/** 설정 화면 공통 카드 틀 — 제목·설명·액션을 세로로 담는다. */
@Composable
private fun SettingsCard(content: @Composable androidx.compose.foundation.layout.ColumnScope.() -> Unit) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceContainer),
    ) {
        Column(
            modifier = Modifier.fillMaxWidth().padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
            content = content,
        )
    }
}

@Composable
private fun ResetConfirmDialog(
    onConfirm: () -> Unit,
    onDismiss: () -> Unit,
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(stringResource(R.string.settings_reset_dialog_title)) },
        text = { Text(stringResource(R.string.settings_reset_dialog_body)) },
        confirmButton = {
            TextButton(onClick = onConfirm) {
                Text(stringResource(R.string.settings_reset_confirm))
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text(stringResource(R.string.settings_reset_cancel))
            }
        },
    )
}
