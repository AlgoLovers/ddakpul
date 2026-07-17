package com.ddakpul.math.data.mapper

import com.ddakpul.math.data.local.entity.ProblemEntity
import com.ddakpul.math.domain.model.Answer
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
    )
