package com.ddakpul.math.core.common

/**
 * 성공/실패를 명시적으로 표현하는 결과 타입. 코틀린 표준 `Result`와 이름이 겹치지 않도록 별도로 둔다.
 * 순수 Kotlin — `android.*` 의존성이 없다.
 */
sealed interface AppResult<out T> {
    data class Success<T>(
        val data: T,
    ) : AppResult<T>

    data class Failure(
        val error: AppError,
    ) : AppResult<Nothing>
}

/** 성공이면 값을, 실패면 null을 돌려준다. UI에서 편하게 분기하기 위한 헬퍼. */
fun <T> AppResult<T>.getOrNull(): T? = (this as? AppResult.Success)?.data

inline fun <T> AppResult<T>.onSuccess(block: (T) -> Unit): AppResult<T> {
    if (this is AppResult.Success) block(data)
    return this
}

inline fun <T> AppResult<T>.onFailure(block: (AppError) -> Unit): AppResult<T> {
    if (this is AppResult.Failure) block(error)
    return this
}
