package com.ddakpul.math.domain.model

/**
 * 한 '풀이 방법'(Problem.methodCode = AA-BB-CC)에 대한 해설 영상.
 * 숫자만 다른 변형·난이도가 같은 방법이면 한 영상을 공유한다(중복 제작 방지).
 *
 * 영상 파일은 APK에 넣지 않고 서버에서 1회 내려받아 캐시한다 — [version]이 오르면
 * 파일명(불변 URL)이 바뀌므로 앱이 새 버전을 다시 받고 옛 캐시를 지운다.
 */
data class SolutionVideo(
    val methodCode: String,
    val title: String,
    /** 원격 다운로드 URL(버전 포함 불변 URL). */
    val url: String,
    /** 영상 개정 번호 — 오르면 재다운로드. */
    val version: Int,
    val durationSec: Int,
)
