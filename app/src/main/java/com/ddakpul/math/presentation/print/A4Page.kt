package com.ddakpul.math.presentation.print

/** A4 지면 규격(포인트, 72dpi) — 워크시트·리포트 PDF 생성기가 공유하는 단일 원본. */
internal object A4Page {
    const val WIDTH = 595
    const val HEIGHT = 842
    const val MARGIN = 40
    const val CONTENT_WIDTH = WIDTH - MARGIN * 2
}
