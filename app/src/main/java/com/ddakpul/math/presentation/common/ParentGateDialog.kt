package com.ddakpul.math.presentation.common

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
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
 * 부모 확인 게이트 — 구매·초기화 같은 어른용 동작 전에 띄운다. '똑똑함 테스트'가 아니라
 * 실수·충동 탭을 막는 '의도된 확인 절차': 보이는 네 자리 숫자를 순서대로 눌러야 통과한다.
 * (사고력 수학을 잘하는 아이도 곱셈은 쉽게 풀기에, 지능 문제 대신 '일부러 하는 동작'으로 둔다.
 * 실제 결제는 구글 플레이가 부모 계정 인증을 다시 요구하므로 이 게이트는 1차 방지선이다.)
 * 순서를 모두 맞히면 [onVerified], 취소하면 [onDismiss].
 */
@Composable
fun ParentGateDialog(
    onVerified: () -> Unit,
    onDismiss: () -> Unit,
) {
    // 서로 다른 네 자리 숫자를 뽑아 그 '순서'를 목표로, 버튼은 자리를 섞어 배치한다.
    val target = remember { (0..9).shuffled(Random).take(4) }
    val buttons = remember(target) { target.shuffled(Random) }
    var progress by remember { mutableIntStateOf(0) }
    var wrong by remember { mutableStateOf(false) }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(stringResource(R.string.parent_gate_title)) },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Text(
                    text = stringResource(R.string.parent_gate_body),
                    style = MaterialTheme.typography.bodyMedium,
                )
                // 목표 순서 — 이미 누른 숫자는 옅게 표시해 진행 상황을 보여준다.
                Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                    target.forEachIndexed { index, digit ->
                        Text(
                            text = digit.toString(),
                            style = MaterialTheme.typography.headlineSmall,
                            fontWeight = FontWeight.Bold,
                            color =
                                if (index < progress) {
                                    MaterialTheme.colorScheme.primary
                                } else {
                                    MaterialTheme.colorScheme.onSurfaceVariant
                                },
                        )
                    }
                }
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    buttons.forEach { digit ->
                        OutlinedButton(
                            onClick = {
                                if (progress < target.size && digit == target[progress]) {
                                    progress += 1
                                    wrong = false
                                    if (progress == target.size) onVerified()
                                } else {
                                    progress = 0
                                    wrong = true
                                }
                            },
                            modifier = Modifier.weight(1f),
                        ) {
                            Text(digit.toString())
                        }
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
