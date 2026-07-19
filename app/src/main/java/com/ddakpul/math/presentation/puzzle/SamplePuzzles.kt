package com.ddakpul.math.presentation.puzzle

import com.ddakpul.math.domain.model.Cell
import com.ddakpul.math.domain.model.DissectionPuzzle

/** 파일럿용 등분 퍼즐 한 개(문항 텍스트 + 도형). 정식 통합 전까지 메모리 시드. */
data class PilotPuzzle(
    val prompt: String,
    val puzzle: DissectionPuzzle,
)

/**
 * 파일럿 시드 — 전부 tools/problemgen/dissection_poc.py로 '해가 정확히 1개(유일해)'임을 사전 검증한
 * 퍼즐이다. 정식 데이터 통합(Room·추천) 전, 새 인터랙션(격자 탭 + 검증기)을 실기기에서 증명하기 위함.
 */
object SamplePuzzles {
    private fun cells(vararg rc: Pair<Int, Int>) = rc.map { Cell(it.first, it.second) }

    val all: List<PilotPuzzle> =
        listOf(
            PilotPuzzle(
                "도형을 똑같은 모양 2조각으로 나눠 보세요.",
                DissectionPuzzle(cells(0 to 0, 0 to 1, 1 to 0, 1 to 1, 2 to 1, 2 to 2), pieceCount = 2),
            ),
            PilotPuzzle(
                "이 도형도 똑같은 모양 2조각으로 나눠 보세요.",
                DissectionPuzzle(
                    cells(0 to 1, 0 to 2, 1 to 0, 1 to 1, 1 to 2, 1 to 3, 2 to 0, 2 to 1, 2 to 2, 2 to 3),
                    pieceCount = 2,
                ),
            ),
            PilotPuzzle(
                "L자를 똑같은 작은 L 4조각으로 나눠 보세요.",
                DissectionPuzzle(
                    cells(
                        0 to 0,
                        0 to 1,
                        1 to 0,
                        1 to 1,
                        2 to 0,
                        2 to 1,
                        2 to 2,
                        2 to 3,
                        3 to 0,
                        3 to 1,
                        3 to 2,
                        3 to 3,
                    ),
                    pieceCount = 4,
                ),
            ),
            PilotPuzzle(
                "똑같은 모양 4조각으로 나누되, 각 조각에 ●·▲·■가 하나씩 들어가게 해 보세요.",
                DissectionPuzzle(
                    cells = (0..1).flatMap { r -> (0..5).map { c -> Cell(r, c) } },
                    pieceCount = 4,
                    symbols =
                        mapOf(
                            Cell(0, 0) to "O",
                            Cell(0, 1) to "O",
                            Cell(0, 2) to "T",
                            Cell(0, 3) to "O",
                            Cell(0, 4) to "O",
                            Cell(0, 5) to "T",
                            Cell(1, 0) to "T",
                            Cell(1, 1) to "S",
                            Cell(1, 2) to "S",
                            Cell(1, 3) to "T",
                            Cell(1, 4) to "S",
                            Cell(1, 5) to "S",
                        ),
                ),
            ),
        )
}
