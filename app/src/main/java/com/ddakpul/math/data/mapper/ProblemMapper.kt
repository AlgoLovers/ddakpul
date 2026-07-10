package com.ddakpul.math.data.mapper

import com.ddakpul.math.data.local.entity.ProblemEntity
import com.ddakpul.math.domain.model.Answer
import com.ddakpul.math.domain.model.MathArea
import com.ddakpul.math.domain.model.Mistake
import com.ddakpul.math.domain.model.Problem
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

private val json = Json { ignoreUnknownKeys = true }
private val stringListSerializer = ListSerializer(String.serializer())
private val mistakeListSerializer = ListSerializer(MistakeDto.serializer())

fun ProblemEntity.toDomain(): Problem =
    Problem(
        id = id,
        grade = grade,
        semester = semester,
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
    )

fun Problem.toEntity(): ProblemEntity =
    ProblemEntity(
        id = id,
        grade = grade,
        semester = semester,
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
    )
