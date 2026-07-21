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
 * 학년 구분은 두지 않는다 — 난이도(Difficulty.MIN..MAX)가 유일한 수준 축이다. 천장은 점진 확장.
 */
data class Problem(
    val id: String,
    val area: MathArea,
    val conceptTags: List<String>,
    val difficulty: Int, // 1~N (Difficulty.MIN..MAX)
    val groupId: String,
    val statement: String,
    val choices: List<String>,
    val answer: Answer,
    val explanation: String?, // 1차 풀이 — 모든 문제가 보유(콘텐츠 규칙, ProblemCatalogTest가 강제). 무료 공개.
    val commonMistakes: List<Mistake>,
    val figure: ProblemFigure? = null,
    /** 2차(심화) 풀이 — 더 깊은 개념·다른 풀이법. 이용권 전용. 없는 문제도 있어 nullable. */
    val detailedExplanation: String? = null,
    /**
     * 계층 관리 코드 AA-BB-CC-DD-SS (영역·유형·방법·난이도·일련). 없으면 null(구 데이터).
     * 앞 8자(AA-BB-CC = [methodCode])가 '풀이 방법' 단위 — 동영상 해설이 이 단위로 붙는다.
     */
    val code: String? = null,
    /**
     * 격자 등분 퍼즐(구성형 문제)이면 여기에 도형이 담긴다. null이면 일반 4지선다.
     * 4지선다와 채점 방식이 달라([ValidateDissectionUseCase]), 이게 있으면 [choices]는 비어 있다.
     */
    val dissection: DissectionPuzzle? = null,
) {
    /** 구성형(격자 등분) 문제 여부 — 화면·채점 분기용. */
    val isDissection: Boolean get() = dissection != null

    /** 동영상 해설이 붙는 '방법' 단위 코드(AA-BB-CC). 코드가 없으면 null. */
    val methodCode: String? get() = code?.takeIf { it.length >= METHOD_CODE_LEN }?.substring(0, METHOD_CODE_LEN)

    companion object {
        /** "AA-BB-CC" = 8자. */
        const val METHOD_CODE_LEN = 8
    }
}
