package com.ddakpul.math.core.common

import kotlin.math.roundToInt

/** 0~1 비율(또는 비율 차)을 정수 퍼센트로. 곳곳의 `(x * 100).roundToInt()` 반복을 단일화. */
fun Float.toPercentInt(): Int = (this * 100).roundToInt()
