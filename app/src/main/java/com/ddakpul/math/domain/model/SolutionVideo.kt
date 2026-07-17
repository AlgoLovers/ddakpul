package com.ddakpul.math.domain.model

/**
 * 한 '풀이 방법'(Problem.methodCode = AA-BB-CC)에 대한 해설 영상.
 * 숫자만 다른 변형·난이도가 같은 방법이면 한 영상을 공유한다(중복 제작 방지).
 */
data class SolutionVideo(
    val methodCode: String,
    val title: String,
    /** 재생에 넘길 URI. 앱 내장은 `asset:///videos/<code>.mp4`, 원격은 https URL. */
    val uri: String,
    val durationSec: Int,
)
