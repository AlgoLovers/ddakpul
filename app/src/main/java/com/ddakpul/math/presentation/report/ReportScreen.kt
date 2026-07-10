package com.ddakpul.math.presentation.report

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
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
import com.ddakpul.math.core.designsystem.component.SectionCard
import com.ddakpul.math.core.designsystem.component.StatTile
import com.ddakpul.math.domain.model.AreaStat
import com.ddakpul.math.domain.model.LearnerReport
import com.ddakpul.math.presentation.common.labelRes
import kotlin.math.roundToInt

@Composable
fun ReportScreen(
    modifier: Modifier = Modifier,
    viewModel: ReportViewModel = hiltViewModel(),
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val report = uiState.report
    if (report == null || report.isEmpty) {
        Box(modifier = modifier.fillMaxSize().padding(24.dp), contentAlignment = Alignment.Center) {
            Text(
                text = stringResource(R.string.report_empty),
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
        return
    }
    ReportContent(report = report, modifier = modifier)
}

@Composable
private fun ReportContent(
    report: LearnerReport,
    modifier: Modifier = Modifier,
) {
    Column(
        modifier = modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        Text(
            text = stringResource(R.string.report_title),
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
        )
        Text(
            text = stringResource(R.string.report_subtitle),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            StatTile(
                label = stringResource(R.string.report_total_solved),
                value = stringResource(R.string.home_unit_count, report.totalSolved),
                modifier = Modifier.weight(1f),
            )
            StatTile(
                label = stringResource(R.string.report_accuracy),
                value = stringResource(R.string.home_unit_percent, (report.accuracy * 100).roundToInt()),
                modifier = Modifier.weight(1f),
            )
            StatTile(
                label = stringResource(R.string.report_current_level),
                value = stringResource(R.string.home_unit_level, report.currentDifficulty),
                modifier = Modifier.weight(1f),
            )
        }

        SectionCard(title = stringResource(R.string.report_area_title)) {
            report.areaStats.forEach { stat -> AreaRow(stat) }
        }
    }
}

@Composable
private fun AreaRow(stat: AreaStat) {
    Column(
        modifier = Modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(6.dp),
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
        ) {
            Text(
                text = stringResource(stat.area.labelRes()),
                style = MaterialTheme.typography.bodyLarge,
                fontWeight = FontWeight.Bold,
            )
            Text(
                text =
                    stringResource(
                        R.string.report_area_stat,
                        stat.correct,
                        stat.solved,
                        (stat.accuracy * 100).roundToInt(),
                    ),
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
        LinearProgressIndicator(
            progress = { stat.accuracy },
            modifier = Modifier.fillMaxWidth(),
        )
    }
}
