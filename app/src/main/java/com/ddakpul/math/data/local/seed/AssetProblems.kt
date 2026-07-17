package com.ddakpul.math.data.local.seed

import com.ddakpul.math.data.mapper.FigureDto
import com.ddakpul.math.data.mapper.toDomain
import com.ddakpul.math.domain.model.Answer
import com.ddakpul.math.domain.model.MathArea
import com.ddakpul.math.domain.model.Mistake
import com.ddakpul.math.domain.model.Problem
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json

/**
 * 생성 파이프라인(tools/problemgen)이 만든 문제은행 JSON의 스키마.
 * [source]는 출처 대장(provenance) — 어디서 어떻게 만들어졌는지 기록한다.
 */
@Serializable
data class AssetMistakeDto(
    val choiceIndex: Int,
    val misconception: String,
)

@Serializable
data class AssetProblemDto(
    val id: String,
    val code: String? = null,
    val area: String,
    val difficulty: Int,
    val groupId: String,
    val concepts: List<String>,
    val statement: String,
    val choices: List<String>,
    val answerIndex: Int,
    val explanation: String? = null,
    val detailedExplanation: String? = null,
    val mistakes: List<AssetMistakeDto> = emptyList(),
    val source: String? = null,
    val figure: FigureDto? = null,
)

@Serializable
data class AssetProblemsFile(
    val version: Int = 1,
    val problems: List<AssetProblemDto> = emptyList(),
)

private val json = Json { ignoreUnknownKeys = true }

/** JSON 텍스트를 도메인 문제 목록으로 변환한다. 테스트에서도 파일을 읽어 직접 호출한다. */
fun parseAssetProblems(text: String): List<Problem> =
    json.decodeFromString(AssetProblemsFile.serializer(), text).problems.map { dto ->
        Problem(
            id = dto.id,
            area = MathArea.valueOf(dto.area),
            conceptTags = dto.concepts,
            difficulty = dto.difficulty,
            groupId = dto.groupId,
            statement = dto.statement,
            choices = dto.choices,
            answer = Answer(dto.answerIndex),
            explanation = dto.explanation,
            commonMistakes = dto.mistakes.map { Mistake(it.choiceIndex, it.misconception) },
            figure = dto.figure?.toDomain(),
            detailedExplanation = dto.detailedExplanation,
            code = dto.code,
        )
    }
