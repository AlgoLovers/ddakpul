package com.ddakpul.math.core.designsystem.component

// 도형 렌더러들이 공유하는 순수 기하 유틸 — android/compose 타입에 의존하지 않아
// 화면 렌더러(ProblemFigureView, Compose Canvas)와 인쇄 렌더러(WorksheetPdfGenerator,
// Android Canvas)가 같은 수학을 함께 쓴다. (예전엔 같은 표가 pipsFor/pdfPips로 두 벌 복붙됐다.)

/** 주사위 눈(1~6) 위치를 면 내부 비율 좌표(0~1)로. */
internal fun dicePips(v: Int): List<Pair<Float, Float>> =
    when (v) {
        1 -> listOf(0.5f to 0.5f)
        2 -> listOf(0.3f to 0.3f, 0.7f to 0.7f)
        3 -> listOf(0.28f to 0.28f, 0.5f to 0.5f, 0.72f to 0.72f)
        4 -> listOf(0.3f to 0.3f, 0.7f to 0.3f, 0.3f to 0.7f, 0.7f to 0.7f)
        5 -> listOf(0.28f to 0.28f, 0.72f to 0.28f, 0.5f to 0.5f, 0.28f to 0.72f, 0.72f to 0.72f)
        6 -> listOf(0.3f to 0.28f, 0.3f to 0.5f, 0.3f to 0.72f, 0.7f to 0.28f, 0.7f to 0.5f, 0.7f to 0.72f)
        else -> emptyList()
    }
