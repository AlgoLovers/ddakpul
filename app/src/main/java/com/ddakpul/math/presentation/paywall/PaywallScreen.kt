package com.ddakpul.math.presentation.paywall

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.ddakpul.math.R
import com.ddakpul.math.core.common.MILLIS_PER_DAY
import com.ddakpul.math.core.designsystem.component.NoticeCard
import com.ddakpul.math.domain.model.Entitlement
import com.ddakpul.math.domain.model.Monetization
import com.ddakpul.math.domain.model.PremiumPass
import com.ddakpul.math.presentation.common.ParentGateDialog
import com.ddakpul.math.presentation.common.launchFreeDeadlineText
import kotlin.math.ceil

private val CONTENT_MAX_WIDTH = 480.dp

/** 이용권(페이월) 화면 — 무료/유료 경계에서 유료 가치를 보여주고 이용권을 활성화한다. */
@Composable
fun PaywallScreen(
    onClose: () -> Unit,
    modifier: Modifier = Modifier,
    viewModel: PaywallViewModel = hiltViewModel(),
) {
    val entitlement by viewModel.entitlement.collectAsStateWithLifecycle()
    val now = remember { System.currentTimeMillis() }
    // 구매 전 부모 확인 게이트 — 어린이 오구매 방지.
    var pendingPass by remember { mutableStateOf<PremiumPass?>(null) }
    pendingPass?.let { pass ->
        ParentGateDialog(
            onVerified = {
                viewModel.activate(pass)
                pendingPass = null
            },
            onDismiss = { pendingPass = null },
        )
    }
    Column(
        modifier = modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Column(
            modifier = Modifier.widthIn(max = CONTENT_MAX_WIDTH).fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(
                    text = stringResource(R.string.paywall_title),
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold,
                )
                TextButton(onClick = onClose) { Text(stringResource(R.string.paywall_close)) }
            }

            if (viewModel.launchFreeUntilMillis > 0L && !entitlement.isPremium(now)) {
                LaunchFreeNoteCard(untilMillis = viewModel.launchFreeUntilMillis)
            }

            if (entitlement.isPremium(now)) {
                ActiveStatusCard(entitlement = entitlement, now = now)
            }

            BenefitsCard()

            if (Monetization.BILLING_ENABLED) {
                // 실결제가 연동된 빌드에서만 구매 UI를 노출한다. 연동 없이 노출하면
                // (1) 공짜 프리미엄이 지급되고 (2) 가격 표기가 사용자·심사자를 오해시킨다.
                PassCard(
                    pass = PremiumPass.ONE_YEAR,
                    titleRes = R.string.paywall_pass_1y_title,
                    highlighted = true,
                    onActivate = { pendingPass = it },
                )
                PassCard(
                    pass = PremiumPass.SIX_MONTHS,
                    titleRes = R.string.paywall_pass_6m_title,
                    highlighted = false,
                    onActivate = { pendingPass = it },
                )
                Text(
                    text = stringResource(R.string.paywall_no_autorenew),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            } else {
                Text(
                    text = stringResource(R.string.paywall_coming_soon),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        }
    }
}

/** 출시 기념 무료 기간 안내 — 지금은 결제하지 않아도 다 열려 있음을 정직하게 알린다. */
@Composable
private fun LaunchFreeNoteCard(untilMillis: Long) {
    NoticeCard(
        title = stringResource(R.string.paywall_launch_free_title),
        body = stringResource(R.string.paywall_launch_free_desc, launchFreeDeadlineText(untilMillis)),
        modifier = Modifier.fillMaxWidth(),
    )
}

@Composable
private fun ActiveStatusCard(
    entitlement: Entitlement,
    now: Long,
) {
    val daysLeft = ceil((entitlement.premiumUntilMillis - now).toDouble() / MILLIS_PER_DAY).toInt().coerceAtLeast(0)
    NoticeCard(
        title = stringResource(R.string.paywall_active_status, daysLeft),
        body = stringResource(R.string.paywall_active_extend),
        modifier = Modifier.fillMaxWidth(),
        containerColor = MaterialTheme.colorScheme.secondaryContainer,
    )
}

@Composable
private fun BenefitsCard() {
    Card(
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceContainer),
        modifier = Modifier.fillMaxWidth(),
    ) {
        Column(
            modifier = Modifier.fillMaxWidth().padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            Text(
                text = stringResource(R.string.paywall_benefits_title),
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
            )
            BenefitRow(R.string.paywall_benefit1)
            BenefitRow(R.string.paywall_benefit2)
            BenefitRow(R.string.paywall_benefit3)
        }
    }
}

@Composable
private fun BenefitRow(textRes: Int) {
    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(text = "✓", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary)
        Text(text = stringResource(textRes), style = MaterialTheme.typography.bodyMedium)
    }
}

@Composable
private fun PassCard(
    pass: PremiumPass,
    titleRes: Int,
    highlighted: Boolean,
    onActivate: (PremiumPass) -> Unit,
) {
    val colors = MaterialTheme.colorScheme
    Card(
        colors =
            CardDefaults.cardColors(
                containerColor = if (highlighted) colors.primaryContainer else colors.surfaceContainer,
                contentColor = if (highlighted) colors.onPrimaryContainer else colors.onSurface,
            ),
        modifier = Modifier.fillMaxWidth(),
    ) {
        Column(
            modifier = Modifier.fillMaxWidth().padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(
                    text = stringResource(titleRes),
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                )
                if (highlighted) {
                    Text(
                        text = stringResource(R.string.paywall_pass_1y_badge),
                        style = MaterialTheme.typography.labelMedium,
                        fontWeight = FontWeight.Bold,
                        color = colors.primary,
                    )
                }
            }
            Text(text = pass.defaultPriceLabel, style = MaterialTheme.typography.headlineSmall)
            Button(onClick = { onActivate(pass) }, modifier = Modifier.fillMaxWidth()) {
                Text(
                    text = stringResource(R.string.paywall_activate),
                    modifier = Modifier.padding(vertical = 4.dp),
                )
            }
        }
    }
}
