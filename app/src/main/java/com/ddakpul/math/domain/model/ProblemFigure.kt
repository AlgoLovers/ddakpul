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

    /**
     * 격자 위 색칠 다각형(넓이 구하기). params: cols, rows(격자 칸 수), n(꼭짓점 수).
     * heights: 꼭짓점 좌표를 [x0,y0,x1,y1,…]로 평탄화(길이 2n, 격자점 0..cols/0..rows).
     */
    GRID_POLYGON,

    /**
     * 삼각형 개수 세기 부채꼴. 한 꼭짓점에서 밑변으로 cevians개의 선을 그어 삼각형을 겹쳐 만든다.
     * params: cevians(내부 선 개수 k → 밑변으로 가는 선은 총 k+2개, 삼각형 (k+2)(k+1)/2개).
     */
    TRIANGLE_FAN,

    /**
     * 정육면체(주사위) 전개도. 6개 면을 격자에 펼치고 각 면에 눈(1~6)을 찍는다. 접었을 때
     * 마주 보는 면 찾기용. params: cols, rows, query(색칠해 물어볼 면의 눈 수).
     * heights: 면마다 [col,row,눈] 3개씩 평탄화(길이 18).
     */
    CUBE_NET,
}

data class ProblemFigure(
    val type: FigureType,
    val params: Map<String, Int> = emptyMap(),
    /** 목록형 데이터(쌓기나무의 칸별 높이 등). 단순 도형은 비어 있다. */
    val heights: List<Int> = emptyList(),
)
