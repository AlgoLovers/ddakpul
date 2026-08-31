package com.ddakpul.math.domain.common

/**
 * 성공/실패를 명시적으로 표현하는 결과 타입. 코틀린 표준 `Result`와 이름이 겹치지 않도록 별도로 둔다.
 * domain 계층 소속 — 순수 Kotlin이며 프레임워크에 의존하지 않는다.
 */
sealed interface AppResult<out T> {
    data class Success<T>(
        val data: T,
    ) : AppResult<T>

    data class Failure(
        val error: AppError,
    ) : AppResult<Nothing>
}
