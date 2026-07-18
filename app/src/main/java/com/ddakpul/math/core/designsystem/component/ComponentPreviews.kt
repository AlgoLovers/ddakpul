package com.ddakpul.math.core.designsystem.component

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.ddakpul.math.core.designsystem.theme.DdakPulTheme

/**
 * 디자인 시스템 컴포넌트 미리보기 — 라이트/다크를 한 파일에서 눈으로 검증한다(Android Studio Preview).
 * 스크린샷 테스트 도구(Paparazzi/Compose Preview Screenshot)를 붙이면 이 @Preview들이 그대로
 * 회귀 테스트가 된다(docs/DESIGN.md). 다크에서 흰 배경+흰 글씨 같은 사고를 여기서 먼저 잡는다.
 */
@Preview(name = "components-light", showBackground = true)
@Preview(name = "components-dark", uiMode = 0x20, showBackground = true) // UI_MODE_NIGHT_YES
@Composable
private fun DesignSystemPreview() {
    DdakPulTheme {
        Surface {
            Column(
                modifier = Modifier.fillMaxWidth().padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    StatTile(label = "푼 문제", value = "306", icon = "📚", modifier = Modifier.weight(1f))
                    StatTile(label = "정답률", value = "85%", icon = "🎯", modifier = Modifier.weight(1f))
                    StatTile(label = "현재 난이도", value = "Lv.9", icon = "🏆", modifier = Modifier.weight(1f))
                }
                SectionCard(title = "영역별 성취", icon = "🧭", subtitle = "네 영역 중 어디가 강한지 한눈에.") {
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        MasteryChip(MasteryStage.MASTERED)
                        MasteryChip(MasteryStage.PRACTICING)
                        MasteryChip(MasteryStage.WEAK)
                        MasteryChip(MasteryStage.NOT_ATTEMPTED)
                    }
                }
            }
        }
    }
}

/** 보기(선택지) 5가지 상태 — 채점 전/후 색이 짝 규칙(onX)을 지키는지 확인. */
@Preview(name = "choices-light", showBackground = true)
@Preview(name = "choices-dark", uiMode = 0x20, showBackground = true)
@Composable
private fun ChoiceOptionsPreview() {
    DdakPulTheme {
        Surface {
            Column(
                modifier = Modifier.fillMaxWidth().padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                ChoiceState.entries.forEachIndexed { i, state ->
                    ChoiceOption(index = i, text = "${'A' + i} 보기 · ${state.name}", state = state, onClick = {}, enabled = true)
                }
            }
        }
    }
}
