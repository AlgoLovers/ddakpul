package com.ddakpul.math.domain.model

/** 정답 — MVP는 4지선다이므로 정답 보기의 인덱스로 표현한다. */
data class Answer(
    val correctChoiceIndex: Int,
)

/**
 * 흔한 오답과 그 오개념. 아이가 [choiceIndex] 보기를 골랐을 때 결과 화면에서 맞춤 피드백을 준다.
 */
data class Mistake(
    val choiceIndex: Int,
    val misconception: String,
)

/**
 * 한 문제. 앱에 사전 생성되어 내장되며(실시간 생성 금지), 추천은 개별 문제가 아니라
 * [groupId]가 같은 묶음(유사 개념·난이도) 단위로 이뤄진다.
 */
data class Problem(
    val id: String,
    val grade: Int, // 4
    val semester: Int, // 2
    val area: MathArea,
    val conceptTags: List<String>,
    val difficulty: Int, // 1~5
    val groupId: String,
    val statement: String,
    val choices: List<String>,
    val answer: Answer,
    val explanation: String?, // 그룹 대표문제만 보유할 수 있다
    val commonMistakes: List<Mistake>,
)
