package com.ddakpul.math.domain.common

/**
 * 도메인 수준의 실패 원인. 예외를 흐름 제어에 쓰지 않고 [AppResult.Failure]에 담아 명시적으로 전달한다.
 * domain 계층 소속 — 순수 Kotlin이며 프레임워크에 의존하지 않는다.
 */
sealed interface AppError {
    /** 문제은행이 비어 있어 추천 자체가 불가능한 상태. */
    data object EmptyProblemBank : AppError

    /** 규칙상 조건에 맞는 다음 문제를 찾지 못한 상태. */
    data object NoProblemAvailable : AppError
}
