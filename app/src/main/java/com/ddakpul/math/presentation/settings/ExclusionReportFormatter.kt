package com.ddakpul.math.presentation.settings

import android.content.Context
import com.ddakpul.math.R
import com.ddakpul.math.domain.model.ExclusionReport
import com.ddakpul.math.presentation.common.labelRes

/**
 * [ExclusionReport]를 사람이 읽을 공유 텍스트로 만든다. 현재 앱 언어의 문자열 리소스를 쓰므로
 * 한국어/영어에 맞춰 나온다(domain은 리소스를 모르니 형식화는 여기서 한다).
 */
fun ExclusionReport.toShareText(context: Context): String {
    val lines =
        entries.map { e ->
            val header =
                if (e.area != null && e.difficulty != null) {
                    context.getString(
                        R.string.feedback_entry_header,
                        e.problemId,
                        context.getString(e.area.labelRes()),
                        e.difficulty,
                    )
                } else {
                    context.getString(R.string.feedback_entry_missing, e.problemId)
                }
            val reason = e.reason?.let { "\n   " + context.getString(R.string.feedback_entry_reason, it) }.orEmpty()
            "${e.order}. $header\n   ${e.statementPreview}$reason"
        }
    return buildString {
        appendLine(context.getString(R.string.feedback_report_title, count))
        appendLine()
        append(lines.joinToString("\n"))
    }
}
