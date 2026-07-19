package com.ddakpul.math.domain.model

/** 격자 한 칸의 위치(행, 열). */
data class Cell(
    val row: Int,
    val col: Int,
)

/**
 * 격자 합동 등분 퍼즐(구성형 문제) — 도형 [cells]를 [pieceCount]개의 '서로 합동인 연결 조각'으로
 * 나누는 공간·사고력 퍼즐. [symbols]가 있으면(응용) 각 조각이 모든 심볼 종류를 하나씩 포함해야 한다.
 *
 * 4지선다와 달리 '정답'을 저장하지 않는다 — 등분 방법이 여럿일 수 있어, 사용자의 배정을
 * [com.ddakpul.math.domain.usecase.ValidateDissectionUseCase]가 규칙으로 검증한다.
 * 문제 저작 단계에서 해가 정확히 1개(유일해)임을 사전 보장한다(tools/problemgen/dissection_poc.py).
 */
data class DissectionPuzzle(
    val cells: List<Cell>,
    val pieceCount: Int,
    val symbols: Map<Cell, String>? = null,
) {
    init {
        require(cells.isNotEmpty()) { "빈 도형" }
        require(pieceCount in 2..cells.size) { "조각 수는 2..칸수" }
        require(cells.size % pieceCount == 0) { "칸수가 조각 수로 나누어떨어져야 함" }
    }

    /** 각 조각의 칸 수. */
    val pieceSize: Int get() = cells.size / pieceCount
}
