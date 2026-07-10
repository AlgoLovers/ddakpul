package com.ddakpul.math.domain.model

/**
 * 초등 수학 교육과정의 4개 영역. 표시용 한글 문자열은 presentation 계층에서 리소스로 매핑한다
 * (domain은 순수 Kotlin이라 `R.string`을 참조하지 않는다).
 */
enum class MathArea {
    NUMBER_OPERATION, // 수와 연산
    CHANGE_RELATION, // 변화와 관계
    SHAPE_MEASUREMENT, // 도형과 측정
    DATA_POSSIBILITY, // 자료와 가능성
}
