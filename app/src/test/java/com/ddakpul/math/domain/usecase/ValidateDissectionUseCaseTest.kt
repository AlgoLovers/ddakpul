package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.model.Cell
import com.ddakpul.math.domain.model.DissectionPuzzle
import com.google.common.truth.Truth.assertThat
import org.junit.Test

class ValidateDissectionUseCaseTest {
    private val validate = ValidateDissectionUseCase()

    private fun cells(vararg rc: Pair<Int, Int>) = rc.map { Cell(it.first, it.second) }

    @Test
    fun verticalDominoes_isValid() {
        // 2x3을 세로 도미노 3개로 — 정답 중 하나
        val puzzle = DissectionPuzzle(cells(0 to 0, 0 to 1, 0 to 2, 1 to 0, 1 to 1, 1 to 2), pieceCount = 3)
        val assign =
            mapOf(
                Cell(0, 0) to 0,
                Cell(1, 0) to 0,
                Cell(0, 1) to 1,
                Cell(1, 1) to 1,
                Cell(0, 2) to 2,
                Cell(1, 2) to 2,
            )
        assertThat(validate(puzzle, assign).isValid).isTrue()
    }

    @Test
    fun mixedOrientationDominoes_congruentUnderRotation_isValid() {
        // 가로 도미노 2개 + 세로 도미노 1개 — 회전하면 모두 합동
        val puzzle = DissectionPuzzle(cells(0 to 0, 0 to 1, 0 to 2, 1 to 0, 1 to 1, 1 to 2), pieceCount = 3)
        val assign =
            mapOf(
                Cell(0, 0) to 0,
                Cell(0, 1) to 0,
                Cell(1, 0) to 1,
                Cell(1, 1) to 1,
                Cell(0, 2) to 2,
                Cell(1, 2) to 2,
            )
        assertThat(validate(puzzle, assign).isValid).isTrue()
    }

    @Test
    fun mirrorImagePieces_congruentUnderReflection_isValid() {
        // L-테트로미노와 그 거울상(J) — 반사까지 허용하므로 합동
        val l = cells(0 to 0, 1 to 0, 2 to 0, 2 to 1)
        val j = cells(0 to 3, 1 to 3, 2 to 3, 2 to 2)
        val puzzle = DissectionPuzzle(l + j, pieceCount = 2)
        val assign = (l.associateWith { 0 } + j.associateWith { 1 })
        assertThat(validate(puzzle, assign).isValid).isTrue()
    }

    @Test
    fun differentShapes_returnsNotCongruent() {
        // L-트로미노 vs I-트로미노 — 크기는 같지만 모양이 다름
        val lTromino = cells(0 to 0, 1 to 0, 1 to 1)
        val iTromino = cells(3 to 0, 3 to 1, 3 to 2)
        val puzzle = DissectionPuzzle(lTromino + iTromino, pieceCount = 2)
        val assign = (lTromino.associateWith { 0 } + iTromino.associateWith { 1 })
        assertThat(validate(puzzle, assign).error).isEqualTo(DissectionError.NOT_CONGRUENT)
    }

    @Test
    fun diagonalCells_returnsDisconnected() {
        val puzzle = DissectionPuzzle(cells(0 to 0, 0 to 1, 1 to 0, 1 to 1), pieceCount = 2)
        val assign =
            mapOf(
                Cell(0, 0) to 0,
                Cell(1, 1) to 0, // 대각선 = 안 이어짐
                Cell(0, 1) to 1,
                Cell(1, 0) to 1,
            )
        assertThat(validate(puzzle, assign).error).isEqualTo(DissectionError.DISCONNECTED)
    }

    @Test
    fun unequalPieceSizes_returnsUnequalSize() {
        val puzzle = DissectionPuzzle(cells(0 to 0, 0 to 1, 0 to 2, 1 to 0, 1 to 1, 1 to 2), pieceCount = 3)
        val assign =
            mapOf(
                Cell(0, 0) to 0,
                Cell(0, 1) to 1,
                Cell(0, 2) to 1,
                Cell(1, 0) to 2,
                Cell(1, 1) to 2,
                Cell(1, 2) to 2,
            )
        assertThat(validate(puzzle, assign).error).isEqualTo(DissectionError.UNEQUAL_SIZE)
    }

    @Test
    fun missingCell_returnsIncomplete() {
        val puzzle = DissectionPuzzle(cells(0 to 0, 0 to 1, 1 to 0, 1 to 1), pieceCount = 2)
        val assign = mapOf(Cell(0, 0) to 0, Cell(0, 1) to 0, Cell(1, 0) to 1) // (1,1) 누락
        assertThat(validate(puzzle, assign).error).isEqualTo(DissectionError.INCOMPLETE)
    }

    @Test
    fun cellOutsideRegion_returnsIncomplete() {
        val puzzle = DissectionPuzzle(cells(0 to 0, 0 to 1), pieceCount = 2)
        val assign = mapOf(Cell(0, 0) to 0, Cell(0, 1) to 1, Cell(9, 9) to 1) // 영역 밖 칸
        assertThat(validate(puzzle, assign).error).isEqualTo(DissectionError.INCOMPLETE)
    }

    @Test
    fun tooFewPieces_returnsWrongPieceCount() {
        val puzzle = DissectionPuzzle(cells(0 to 0, 0 to 1, 0 to 2, 1 to 0, 1 to 1, 1 to 2), pieceCount = 3)
        val assign =
            mapOf(
                Cell(0, 0) to 0,
                Cell(0, 1) to 0,
                Cell(0, 2) to 0,
                Cell(1, 0) to 1,
                Cell(1, 1) to 1,
                Cell(1, 2) to 1,
            )
        assertThat(validate(puzzle, assign).error).isEqualTo(DissectionError.WRONG_PIECE_COUNT)
    }

    @Test
    fun symbolsOnePerPiece_isValid() {
        // 두 가로 조각, 각 조각에 O·T·S 하나씩
        val region = cells(0 to 0, 0 to 1, 0 to 2, 1 to 0, 1 to 1, 1 to 2)
        val symbols =
            mapOf(
                Cell(0, 0) to "O",
                Cell(0, 1) to "T",
                Cell(0, 2) to "S",
                Cell(1, 0) to "T",
                Cell(1, 1) to "S",
                Cell(1, 2) to "O",
            )
        val puzzle = DissectionPuzzle(region, pieceCount = 2, symbols = symbols)
        val assign =
            mapOf(
                Cell(0, 0) to 0,
                Cell(0, 1) to 0,
                Cell(0, 2) to 0,
                Cell(1, 0) to 1,
                Cell(1, 1) to 1,
                Cell(1, 2) to 1,
            )
        assertThat(validate(puzzle, assign).isValid).isTrue()
    }

    @Test
    fun symbolMissingType_returnsSymbol() {
        // 조각0 = O,T,T (S 빠지고 T 중복) → 위반
        val region = cells(0 to 0, 0 to 1, 0 to 2, 1 to 0, 1 to 1, 1 to 2)
        val symbols =
            mapOf(
                Cell(0, 0) to "O",
                Cell(0, 1) to "T",
                Cell(0, 2) to "T",
                Cell(1, 0) to "S",
                Cell(1, 1) to "S",
                Cell(1, 2) to "O",
            )
        val puzzle = DissectionPuzzle(region, pieceCount = 2, symbols = symbols)
        val assign =
            mapOf(
                Cell(0, 0) to 0,
                Cell(0, 1) to 0,
                Cell(0, 2) to 0,
                Cell(1, 0) to 1,
                Cell(1, 1) to 1,
                Cell(1, 2) to 1,
            )
        assertThat(validate(puzzle, assign).error).isEqualTo(DissectionError.SYMBOL)
    }
}
