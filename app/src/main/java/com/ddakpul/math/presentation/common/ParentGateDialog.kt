package com.ddakpul.math.presentation.common

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.ddakpul.math.R
import kotlin.random.Random

/**
 * 부모 확인 게이트 — 구매·초기화 같은 어른용 동작 전에 띄운다. 어린이가 혼자 통과하기 어렵도록
 * 두 자리 곱셈을 4지선다로 낸다(저장된 PIN이 아니라 매번 새 문제 = Play 패밀리 권장 방식).
 * 정답을 고르면 [onVerified], 취소하면 [onDismiss].
 */
@Composable
fun ParentGateDialog(
    onVerified: () -> Unit,
    onDismiss: () -> Unit,
) {
    // 다이얼로그가 뜰 때 한 번만 문제를 뽑는다(재구성에도 안 바뀌게 remember).
    val problem =
        remember {
            val a = Random.nextInt(6, 10)
            val b = Random.nextInt(6, 10)
            val answer = a * b
            val options = linkedSetOf(answer)
            while (options.size < 4) {
                val delta = Random.nextInt(-9, 10)
                if (delta != 0) options.add((answer + delta).coerceAtLeast(10))
            }
            Triple(a to b, answer, options.toList().shuffled())
        }
    val (ab, answer, options) = problem
    var wrong by remember { mutableStateOf(false) }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(stringResource(R.string.parent_gate_title)) },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(
                    text = stringResource(R.string.parent_gate_body),
                    style = MaterialTheme.typography.bodyMedium,
                )
                Text(
                    text = stringResource(R.string.parent_gate_question, ab.first, ab.second),
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold,
                )
                options.forEach { option ->
                    OutlinedButton(
                        onClick = { if (option == answer) onVerified() else wrong = true },
                        modifier = Modifier.fillMaxWidth(),
                    ) {
                        Text(option.toString())
                    }
                }
                if (wrong) {
                    Text(
                        text = stringResource(R.string.parent_gate_retry),
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.error,
                    )
                }
            }
        },
        confirmButton = {},
        dismissButton = {
            TextButton(onClick = onDismiss) { Text(stringResource(R.string.parent_gate_cancel)) }
        },
    )
}
