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
 * 학년 구분은 두지 않는다 — 난이도(1~7)가 유일한 수준 축이다.
 */
data class Problem(
    val id: String,
    val area: MathArea,
    val conceptTags: List<String>,
    val difficulty: Int, // 1~7
    val groupId: String,
    val statement: String,
    val choices: List<String>,
    val answer: Answer,
    val explanation: String?, // 1차 풀이 — 모든 문제가 보유(콘텐츠 규칙, ProblemCatalogTest가 강제). 무료 공개.
    val commonMistakes: List<Mistake>,
    val figure: ProblemFigure? = null,
    /** 2차(심화) 풀이 — 더 깊은 개념·다른 풀이법. 이용권 전용. 없는 문제도 있어 nullable. */
    val detailedExplanation: String? = null,
)
