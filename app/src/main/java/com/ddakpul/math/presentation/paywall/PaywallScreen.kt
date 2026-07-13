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
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.ddakpul.math.R
import com.ddakpul.math.domain.model.Entitlement
import com.ddakpul.math.domain.model.PremiumPass
import kotlin.math.ceil

private const val MILLIS_PER_DAY = 86_400_000L
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
    Column(
        modifier = modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Column(
            modifier = Modifier.fillMaxWidth().widthIn(max = CONTENT_MAX_WIDTH),
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

            if (entitlement.isPremium(now)) {
                ActiveStatusCard(entitlement = entitlement, now = now)
            }

            BenefitsCard()

            PassCard(
                pass = PremiumPass.ONE_YEAR,
                titleRes = R.string.paywall_pass_1y_title,
                highlighted = true,
                onActivate = viewModel::activate,
            )
            PassCard(
                pass = PremiumPass.SIX_MONTHS,
                titleRes = R.string.paywall_pass_6m_title,
                highlighted = false,
                onActivate = viewModel::activate,
            )

            Text(
                text = stringResource(R.string.paywall_no_autorenew),
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Text(
                text = stringResource(R.string.paywall_test_note),
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

@Composable
private fun ActiveStatusCard(
    entitlement: Entitlement,
    now: Long,
) {
    val daysLeft = ceil((entitlement.premiumUntilMillis - now).toDouble() / MILLIS_PER_DAY).toInt().coerceAtLeast(0)
    Card(
        colors =
            CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.secondaryContainer,
                contentColor = MaterialTheme.colorScheme.onSecondaryContainer,
            ),
        modifier = Modifier.fillMaxWidth(),
    ) {
        Column(
            modifier = Modifier.fillMaxWidth().padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(4.dp),
        ) {
            Text(
                text = stringResource(R.string.paywall_active_status, daysLeft),
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
            )
            Text(
                text = stringResource(R.string.paywall_active_extend),
                style = MaterialTheme.typography.bodyMedium,
            )
        }
    }
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
