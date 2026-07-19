package com.ddakpul.math.presentation.puzzle

import androidx.lifecycle.ViewModel
import com.ddakpul.math.domain.model.Cell
import com.ddakpul.math.domain.usecase.DissectionValidation
import com.ddakpul.math.domain.usecase.ValidateDissectionUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import javax.inject.Inject

/** 공간 퍼즐(격자 등분) 화면의 단일 불변 상태. */
data class DissectionUiState(
    val index: Int,
    val total: Int,
    val pilot: PilotPuzzle,
    val selectedPiece: Int = 0,
    val assignment: Map<Cell, Int> = emptyMap(),
    val result: DissectionValidation? = null,
)

/**
 * 공간 퍼즐 파일럿 ViewModel — 메모리 시드([SamplePuzzles])를 순회하며, 사용자의 '칸→조각' 배정을
 * 모아 [ValidateDissectionUseCase]로 채점한다. MC 뱅크·추천·DB와 무관한 독립 화면(파일럿).
 */
@HiltViewModel
class DissectionPuzzleViewModel
    @Inject
    constructor(
        private val validate: ValidateDissectionUseCase,
    ) : ViewModel() {
        private val puzzles = SamplePuzzles.all
        private val _uiState = MutableStateFlow(stateFor(0))
        val uiState: StateFlow<DissectionUiState> = _uiState.asStateFlow()

        private fun stateFor(index: Int) = DissectionUiState(index = index, total = puzzles.size, pilot = puzzles[index])

        /** 팔레트에서 칠할 조각 색을 고른다. */
        fun selectPiece(pieceId: Int) = _uiState.update { it.copy(selectedPiece = pieceId, result = null) }

        /** 칸을 탭 — 선택한 조각으로 칠하고, 같은 조각을 다시 탭하면 지운다(토글). */
        fun tapCell(cell: Cell) =
            _uiState.update { s ->
                val next =
                    if (s.assignment[cell] == s.selectedPiece) {
                        s.assignment - cell
                    } else {
                        s.assignment + (cell to s.selectedPiece)
                    }
                s.copy(assignment = next, result = null)
            }

        fun clear() = _uiState.update { it.copy(assignment = emptyMap(), result = null) }

        fun check() = _uiState.update { it.copy(result = validate(it.pilot.puzzle, it.assignment)) }

        fun next() = _uiState.update { stateFor((it.index + 1) % puzzles.size) }
    }
