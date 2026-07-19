package com.ddakpul.math.data.mapper

import com.ddakpul.math.data.local.entity.ProblemEntity
import com.ddakpul.math.domain.model.Answer
import com.ddakpul.math.domain.model.Cell
import com.ddakpul.math.domain.model.DissectionPuzzle
import com.ddakpul.math.domain.model.FigureType
import com.ddakpul.math.domain.model.MathArea
import com.ddakpul.math.domain.model.Mistake
import com.ddakpul.math.domain.model.Problem
import com.ddakpul.math.domain.model.ProblemFigure
import kotlinx.serialization.Serializable
import kotlinx.serialization.builtins.ListSerializer
import kotlinx.serialization.builtins.serializer
import kotlinx.serialization.json.Json

/** 흔한 오답의 data 계층 직렬화용 DTO — domain 모델을 직렬화 프레임워크에 묶지 않기 위함. */
@Serializable
private data class MistakeDto(
    val choiceIndex: Int,
    val misconception: String,
)

/** 도형 지시서 직렬화 DTO. type은 [FigureType] 이름. */
@Serializable
data class FigureDto(
    val type: String,
    val params: Map<String, Int> = emptyMap(),
    val heights: List<Int> = emptyList(),
)

/** 격자 등분 퍼즐 직렬화 DTO — Room JSON 컬럼용. cells=[r,c] 쌍, symbols=[r,c,sym] 삼중. */
@Serializable
data class DissectionDto(
    val cells: List<List<Int>>,
    val pieceCount: Int,
    val symbols: List<SymbolDto> = emptyList(),
) {
    @Serializable
    data class SymbolDto(
        val r: Int,
        val c: Int,
        val sym: String,
    )
}

internal fun DissectionDto.toDomain(): DissectionPuzzle =
    DissectionPuzzle(
        cells = cells.map { Cell(it[0], it[1]) },
        pieceCount = pieceCount,
        symbols = symbols.takeIf { it.isNotEmpty() }?.associate { Cell(it.r, it.c) to it.sym },
    )

private fun DissectionPuzzle.toDto(): DissectionDto =
    DissectionDto(
        cells = cells.map { listOf(it.row, it.col) },
        pieceCount = pieceCount,
        symbols = symbols.orEmpty().map { (cell, sym) -> DissectionDto.SymbolDto(cell.row, cell.col, sym) },
    )

private val json = Json { ignoreUnknownKeys = true }
private val stringListSerializer = ListSerializer(String.serializer())
private val mistakeListSerializer = ListSerializer(MistakeDto.serializer())

internal fun FigureDto.toDomain(): ProblemFigure = ProblemFigure(FigureType.valueOf(type), params, heights)

private fun ProblemFigure.toDto(): FigureDto = FigureDto(type.name, params, heights)

fun ProblemEntity.toDomain(): Problem =
    Problem(
        id = id,
        area = MathArea.valueOf(area),
        conceptTags = json.decodeFromString(stringListSerializer, conceptTagsJson),
        difficulty = difficulty,
        groupId = groupId,
        statement = statement,
        choices = json.decodeFromString(stringListSerializer, choicesJson),
        answer = Answer(correctChoiceIndex),
        explanation = explanation,
        commonMistakes =
            json
                .decodeFromString(mistakeListSerializer, mistakesJson)
                .map { Mistake(it.choiceIndex, it.misconception) },
        figure = figureJson?.let { json.decodeFromString(FigureDto.serializer(), it).toDomain() },
        detailedExplanation = detailedExplanation,
        code = code,
        dissection = dissectionJson?.let { json.decodeFromString(DissectionDto.serializer(), it).toDomain() },
    )

fun Problem.toEntity(): ProblemEntity =
    ProblemEntity(
        id = id,
        area = area.name,
        conceptTagsJson = json.encodeToString(stringListSerializer, conceptTags),
        difficulty = difficulty,
        groupId = groupId,
        statement = statement,
        choicesJson = json.encodeToString(stringListSerializer, choices),
        correctChoiceIndex = answer.correctChoiceIndex,
        explanation = explanation,
        mistakesJson =
            json.encodeToString(
                mistakeListSerializer,
                commonMistakes.map { MistakeDto(it.choiceIndex, it.misconception) },
            ),
        figureJson = figure?.let { json.encodeToString(FigureDto.serializer(), it.toDto()) },
        detailedExplanation = detailedExplanation,
        code = code,
        dissectionJson = dissection?.let { json.encodeToString(DissectionDto.serializer(), it.toDto()) },
    )
