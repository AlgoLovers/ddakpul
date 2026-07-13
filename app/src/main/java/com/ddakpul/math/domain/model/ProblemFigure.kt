package com.ddakpul.math.domain.model

/**
 * 문제에 딸린 도형 지시서. 이미지 파일 대신 타입+파라미터만 저장하고,
 * 화면(Compose Canvas)과 인쇄(PDF Canvas)가 각자 렌더링한다 — 해상도 무관·용량 0.
 */
enum class FigureType {
    /** 시계 면. params: hour(1~12), minute(0~59). 눈금만 있는 시계(숫자 없음). */
    CLOCK,

    /** 속이 빈 정사각형 바둑돌 배열. params: side(한 변의 돌 개수). */
    DOT_BORDER,

    /** 격자(바둑판 길). params: w, h(칸 수), mark(1이면 출발·도착 표시). */
    GRID,

    /** L자 도형(모퉁이 잘린 정사각형). params: w, h(전체 변), cutW, cutH(잘린 변). 단위는 cm 라벨. */
    L_SHAPE,

    /** 정다각형. params: n(변 수 3~12), diagonals(1이면 대각선도 그린다). */
    POLYGON,

    /** 쌓기나무(입체 등각도). params: w(가로 칸), d(세로 칸). heights: 칸별 높이(row-major, 길이 w*d). */
    CUBE_STACK,
}

data class ProblemFigure(
    val type: FigureType,
    val params: Map<String, Int> = emptyMap(),
    /** 목록형 데이터(쌓기나무의 칸별 높이 등). 단순 도형은 비어 있다. */
    val heights: List<Int> = emptyList(),
)
