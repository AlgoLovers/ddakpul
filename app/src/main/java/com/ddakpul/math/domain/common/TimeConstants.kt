package com.ddakpul.math.domain.common

/**
 * 하루의 밀리초. 경과 일수·복습 스케줄·통계 창 계산이 공유하는 단일 상수.
 * 예전엔 도메인·데이터·프레젠테이션 5곳에 각각 정의(일부는 `24L * 60 * 60 * 1000` 형태)돼 있었다.
 */
const val MILLIS_PER_DAY = 86_400_000L
