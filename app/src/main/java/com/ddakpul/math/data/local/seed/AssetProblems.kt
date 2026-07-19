package com.ddakpul.math.data.local.seed

import com.ddakpul.math.data.mapper.FigureDto
import com.ddakpul.math.data.mapper.toDomain
import com.ddakpul.math.domain.model.Answer
import com.ddakpul.math.domain.model.Cell
import com.ddakpul.math.domain.model.DissectionPuzzle
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

// ── 격자 등분 퍼즐(구성형 문제) — 별도 에셋(problems_dissection.json). 4지선다 스키마와 달라 따로 파싱한다. ──

@Serializable
data class DissectionSymbolDto(
    val r: Int,
    val c: Int,
    val sym: String,
)

@Serializable
data class DissectionProblemDto(
    val id: String,
    val area: String,
    val difficulty: Int,
    val groupId: String,
    val pieceCount: Int,
    val cells: List<List<Int>>,
    val symbols: List<DissectionSymbolDto> = emptyList(),
)

@Serializable
data class DissectionFile(
    val version: Int = 1,
    val problems: List<DissectionProblemDto> = emptyList(),
)

/**
 * 등분 퍼즐 JSON을 도메인 문제로 변환한다. 문장은 저장돼 있지 않고 조각 수·심볼 유무로 지역화한다
 * ([english]). 정답은 없다(choices 비움) — [com.ddakpul.math.domain.usecase.ValidateDissectionUseCase]가 채점.
 */
fun parseDissectionProblems(
    text: String,
    english: Boolean,
): List<Problem> =
    json.decodeFromString(DissectionFile.serializer(), text).problems.map { dto ->
        val hasSymbols = dto.symbols.isNotEmpty()
        Problem(
            id = dto.id,
            area = MathArea.valueOf(dto.area),
            conceptTags = listOf(if (english) "spatial dissection" else "합동 등분"),
            difficulty = dto.difficulty,
            groupId = dto.groupId,
            statement = dissectionStatement(dto.pieceCount, hasSymbols, english),
            choices = emptyList(),
            answer = Answer(-1),
            explanation = null,
            commonMistakes = emptyList(),
            dissection =
                DissectionPuzzle(
                    cells = dto.cells.map { Cell(it[0], it[1]) },
                    pieceCount = dto.pieceCount,
                    symbols = dto.symbols.takeIf { it.isNotEmpty() }?.associate { Cell(it.r, it.c) to it.sym },
                ),
        )
    }

private fun dissectionStatement(
    pieceCount: Int,
    hasSymbols: Boolean,
    english: Boolean,
): String =
    when {
        english && hasSymbols -> "Divide the shape into $pieceCount identical pieces so each piece has one ●, ▲, and ■."
        english -> "Divide the shape into $pieceCount identical pieces."
        hasSymbols -> "똑같은 모양 ${pieceCount}조각으로 나누되, 각 조각에 ●·▲·■가 하나씩 들어가게 해 보세요."
        else -> "도형을 똑같은 모양 ${pieceCount}조각으로 나눠 보세요."
    }
