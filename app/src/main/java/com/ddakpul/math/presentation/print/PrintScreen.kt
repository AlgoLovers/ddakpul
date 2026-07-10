package com.ddakpul.math.presentation.print

import android.content.Context
import android.print.PrintAttributes
import android.print.PrintManager
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Print
import androidx.compose.material3.Button
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.ddakpul.math.R
import com.ddakpul.math.core.designsystem.component.SectionCard
import com.ddakpul.math.domain.model.MathArea
import com.ddakpul.math.domain.model.Problem
import com.ddakpul.math.domain.usecase.WorksheetSource
import com.ddakpul.math.presentation.common.labelRes
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PrintScreen(
    onBack: () -> Unit,
    modifier: Modifier = Modifier,
    viewModel: PrintViewModel = hiltViewModel(),
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val snackbarHostState = remember { SnackbarHostState() }
    val areaLabels = MathArea.entries.associateWith { stringResource(it.labelRes()) }
    val texts = worksheetTexts(areaLabels)
    val emptyMessage = stringResource(R.string.print_empty)

    Scaffold(
        modifier = modifier.fillMaxSize(),
        topBar = {
            TopAppBar(
                title = { Text(stringResource(R.string.print_title)) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = stringResource(R.string.print_back),
                        )
                    }
                },
            )
        },
        snackbarHost = { SnackbarHost(snackbarHostState) },
    ) { innerPadding ->
        Box(
            modifier = Modifier.fillMaxSize().padding(innerPadding),
            contentAlignment = Alignment.TopCenter,
        ) {
            PrintOptionsBody(
                uiState = uiState,
                areaLabels = areaLabels,
                onCountChange = viewModel::setCount,
                onSourceChange = viewModel::setSource,
                onAreaChange = viewModel::setArea,
                onToggleAnswers = viewModel::toggleIncludeAnswers,
                onPrint = {
                    scope.launch {
                        val problems = viewModel.buildProblems()
                        if (problems.isEmpty()) {
                            snackbarHostState.showSnackbar(emptyMessage)
                        } else {
                            printWorksheet(context, problems, uiState.includeAnswers, texts)
                        }
                    }
                },
            )
        }
    }
}

@Composable
private fun PrintOptionsBody(
    uiState: PrintUiState,
    areaLabels: Map<MathArea, String>,
    onCountChange: (Int) -> Unit,
    onSourceChange: (WorksheetSource) -> Unit,
    onAreaChange: (MathArea?) -> Unit,
    onToggleAnswers: () -> Unit,
    onPrint: () -> Unit,
) {
    Column(
        modifier =
            Modifier
                .widthIn(max = 640.dp)
                .fillMaxWidth()
                .verticalScroll(rememberScrollState())
                .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        Text(
            text = stringResource(R.string.print_subtitle),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )

        SectionCard(title = stringResource(R.string.print_count_label)) {
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                PrintUiState.COUNT_OPTIONS.forEach { option ->
                    FilterChip(
                        selected = uiState.count == option,
                        onClick = { onCountChange(option) },
                        label = { Text(stringResource(R.string.print_count_option, option)) },
                    )
                }
            }
        }

        SectionCard(title = stringResource(R.string.print_source_label)) {
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                FilterChip(
                    selected = uiState.source == WorksheetSource.RECOMMENDED,
                    onClick = { onSourceChange(WorksheetSource.RECOMMENDED) },
                    label = { Text(stringResource(R.string.print_source_recommended)) },
                )
                FilterChip(
                    selected = uiState.source == WorksheetSource.WRONG_FIRST,
                    onClick = { onSourceChange(WorksheetSource.WRONG_FIRST) },
                    label = { Text(stringResource(R.string.print_source_wrong)) },
                )
            }
        }

        SectionCard(title = stringResource(R.string.print_area_label)) {
            Row(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                modifier = Modifier.fillMaxWidth(),
            ) {
                FilterChip(
                    selected = uiState.area == null,
                    onClick = { onAreaChange(null) },
                    label = { Text(stringResource(R.string.print_area_all)) },
                )
            }
            Row(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                modifier = Modifier.fillMaxWidth(),
            ) {
                MathArea.entries.forEach { area ->
                    FilterChip(
                        selected = uiState.area == area,
                        onClick = { onAreaChange(area) },
                        label = { Text(areaLabels.getValue(area)) },
                    )
                }
            }
        }

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text(
                text = stringResource(R.string.print_include_answers),
                style = MaterialTheme.typography.bodyLarge,
                fontWeight = FontWeight.Bold,
            )
            Switch(
                checked = uiState.includeAnswers,
                onCheckedChange = { onToggleAnswers() },
            )
        }

        Button(
            onClick = onPrint,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Icon(imageVector = Icons.Filled.Print, contentDescription = null)
            Text(
                text = stringResource(R.string.print_action),
                style = MaterialTheme.typography.titleMedium,
                modifier = Modifier.padding(vertical = 6.dp, horizontal = 8.dp),
            )
        }
    }
}

@Composable
private fun worksheetTexts(areaLabels: Map<MathArea, String>): WorksheetTexts =
    WorksheetTexts(
        title = stringResource(R.string.worksheet_title),
        nameLine = stringResource(R.string.worksheet_name_line),
        dateLine = stringResource(R.string.worksheet_date_line),
        answerTitle = stringResource(R.string.worksheet_answer_title),
        footer = stringResource(R.string.worksheet_footer),
        solutionSpaceLabel = stringResource(R.string.worksheet_solution_space),
        areaLabels = areaLabels,
    )

/** 안드로이드 인쇄 프레임워크로 학습지 인쇄 잡을 시작한다. */
private fun printWorksheet(
    context: Context,
    problems: List<Problem>,
    includeAnswers: Boolean,
    texts: WorksheetTexts,
) {
    val printManager = context.getSystemService(Context.PRINT_SERVICE) as PrintManager
    val jobName = context.getString(R.string.print_job_name)
    val adapter =
        WorksheetPrintAdapter(fileName = "ddakpul-worksheet.pdf") {
            WorksheetPdfGenerator(problems, includeAnswers, texts).generate()
        }
    val attributes =
        PrintAttributes
            .Builder()
            .setMediaSize(PrintAttributes.MediaSize.ISO_A4)
            .build()
    printManager.print(jobName, adapter, attributes)
}
