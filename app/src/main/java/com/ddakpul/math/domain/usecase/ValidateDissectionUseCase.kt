package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.model.Cell
import com.ddakpul.math.domain.model.DissectionPuzzle
import javax.inject.Inject

/** 등분 검증 실패 사유 — 화면 힌트 문구로 매핑된다. */
enum class DissectionError {
    INCOMPLETE, // 모든 칸을 정확히 한 조각에 배정하지 않음
    WRONG_PIECE_COUNT, // 조각 수가 목표와 다름
    UNEQUAL_SIZE, // 조각들의 칸 수가 다름
    DISCONNECTED, // 어떤 조각이 한 덩어리로 안 이어짐
    NOT_CONGRUENT, // 조각들의 모양이 서로 합동이 아님(회전·반사까지)
    SYMBOL, // 각 조각에 심볼이 하나씩 들어가지 않음
}

/** 등분 검증 결과. */
data class DissectionValidation(
    val isValid: Boolean,
    val error: DissectionError? = null,
)

/**
 * 격자 합동 등분 퍼즐 채점기 — 사용자의 '칸→조각번호' 배정이 유효한 등분인지 규칙으로 판정한다.
 * 정답을 저장·비교하지 않고 (1)전체 덮기 (2)조각 수·크기 (3)각 조각 연결 (4)조각 간 합동
 * (5)심볼 제약을 직접 검사한다. 순수 함수 — tools/problemgen/dissection_poc.py의 Kotlin 이식.
 */
class ValidateDissectionUseCase
    @Inject
    constructor() {
        operator fun invoke(
            puzzle: DissectionPuzzle,
            assignment: Map<Cell, Int>,
        ): DissectionValidation {
            if (assignment.keys != puzzle.cells.toSet()) return fail(DissectionError.INCOMPLETE)

            val pieces = assignment.entries.groupBy({ it.value }, { it.key })
            if (pieces.size != puzzle.pieceCount) return fail(DissectionError.WRONG_PIECE_COUNT)
            if (pieces.values
                    .map { it.size }
                    .toSet()
                    .size != 1
            ) {
                return fail(DissectionError.UNEQUAL_SIZE)
            }
            if (pieces.values.any { !isConnected(it) }) return fail(DissectionError.DISCONNECTED)
            if (pieces.values
                    .map { canonicalKey(it) }
                    .toSet()
                    .size != 1
            ) {
                return fail(DissectionError.NOT_CONGRUENT)
            }

            puzzle.symbols?.let { symbols ->
                val types = symbols.values.toSet()
                for (piece in pieces.values) {
                    val got = piece.mapNotNull { symbols[it] }
                    if (got.size != types.size || got.toSet().size != types.size) return fail(DissectionError.SYMBOL)
                }
            }
            return DissectionValidation(true)
        }

        private fun fail(e: DissectionError) = DissectionValidation(false, e)

        /** 상하좌우 인접만으로 한 덩어리인지(BFS). */
        private fun isConnected(cells: List<Cell>): Boolean {
            val set = cells.toHashSet()
            if (set.isEmpty()) return true
            val seen = HashSet<Cell>()
            val stack = ArrayDeque<Cell>()
            val start = set.first()
            seen.add(start)
            stack.addLast(start)
            while (stack.isNotEmpty()) {
                val (r, c) = stack.removeLast()
                for (d in NEIGHBORS) {
                    val nb = Cell(r + d.row, c + d.col)
                    if (nb in set && seen.add(nb)) stack.addLast(nb)
                }
            }
            return seen.size == set.size
        }

        /**
         * 폴리오미노의 표준형 문자열 — 8개 강체변환(회전4×반사2) 각각을 정규화(좌상단 원점 이동)한 뒤
         * 사전순 최소를 고른다. 두 조각이 합동 ⇔ 표준형이 같다.
         */
        private fun canonicalKey(cells: List<Cell>): String = TRANSFORMS.minOf { t -> normalizedKey(cells.map(t)) }

        private fun normalizedKey(cells: List<Cell>): String {
            val minRow = cells.minOf { it.row }
            val minCol = cells.minOf { it.col }
            return cells
                .map { Cell(it.row - minRow, it.col - minCol) }
                .sortedWith(compareBy({ it.row }, { it.col }))
                .joinToString(";") { "${it.row},${it.col}" }
        }

        private companion object {
            val NEIGHBORS = listOf(Cell(1, 0), Cell(-1, 0), Cell(0, 1), Cell(0, -1))

            /** 정사각 격자 위 8개 대칭: 회전 0·90·180·270 × 반사. */
            val TRANSFORMS: List<(Cell) -> Cell> =
                listOf(
                    { c: Cell -> Cell(c.row, c.col) },
                    { c: Cell -> Cell(-c.col, c.row) },
                    { c: Cell -> Cell(-c.row, -c.col) },
                    { c: Cell -> Cell(c.col, -c.row) },
                    { c: Cell -> Cell(c.row, -c.col) },
                    { c: Cell -> Cell(-c.col, -c.row) },
                    { c: Cell -> Cell(-c.row, c.col) },
                    { c: Cell -> Cell(c.col, c.row) },
                )
        }
    }
