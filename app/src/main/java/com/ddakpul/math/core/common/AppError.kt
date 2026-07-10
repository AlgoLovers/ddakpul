package com.ddakpul.math.core.common

/**
 * 도메인 수준의 실패 원인. 예외를 흐름 제어에 쓰지 않고 [AppResult.Failure]에 담아 명시적으로 전달한다.
 * 순수 Kotlin — `android.*` 의존성이 없다.
 */
sealed interface AppError {
    /** 문제은행이 비어 있어 추천 자체가 불가능한 상태. */
    data object EmptyProblemBank : AppError

    /** 규칙상 조건에 맞는 다음 문제를 찾지 못한 상태. */
    data object NoProblemAvailable : AppError

    /** 그 밖의 예기치 못한 실패. */
    data class Unexpected(
        val cause: Throwable? = null,
    ) : AppError
}
