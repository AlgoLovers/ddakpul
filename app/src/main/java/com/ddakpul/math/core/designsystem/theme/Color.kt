package com.ddakpul.math.core.designsystem.theme

import androidx.compose.ui.graphics.Color

// 딱풀 밝은 팔레트(2026-07 리디자인) — 토스·카카오식 "밝고 깨끗".
// 원리: 부드러운 연회색 캔버스 + 흰 카드(눈부시지 않게 뜬다) + 밝은 포인트색 하나 + 차콜 텍스트.
// 채색 큰 블록·무거운 그림자·탁한 색을 피해 '칙칙함'을 없앤다. 색은 CTA·핵심 강조에만 아껴 쓴다.

// ── 포인트색(Primary) — 밝은 인디고-바이올렛 ──
val Accent = Color(0xFF5B5EF0)
val AccentSoft = Color(0xFFECEDFF) // primaryContainer(연한 강조 배경)
val AccentDark = Color(0xFF2C2F9E) // onPrimaryContainer(연배경 위 글자)
val AccentLight = Color(0xFFAFB0FF) // 다크 테마 primary

// ── 정답/성공(Secondary) — 민트 ──
val Mint = Color(0xFF12B26E)
val MintSoft = Color(0xFFDBF6EA)
val MintDark = Color(0xFF05663F)
val MintLight = Color(0xFF6FE0B0)

// ── 안내·프로모(Tertiary) — 앰버 ──
val Amber = Color(0xFFC77D0E)
val AmberSoft = Color(0xFFFFF2DC)

// 크림 배경 위 앰버 텍스트(라이트 onTertiaryContainer). 이전 #5E3B00은 진갈색이라 칙칙 →
// 따뜻한 앰버-캐러멜로 밝힘(대비 ~4.9:1로 AA 유지). 다크 테마 앰버 텍스트는 별도 색.
val AmberDark = Color(0xFF9A5B00)
val AmberLight = Color(0xFFFFC46A)

// ── 오답·오류(Error) — 코랄 ──
val Coral = Color(0xFFE84C46)
val CoralSoft = Color(0xFFFDEBEA)
val CoralDark = Color(0xFF7A1712)
val CoralLight = Color(0xFFFFB4AD)

// ── 무채색: 라이트(연회색 캔버스 + 흰 카드) ──
val CanvasLight = Color(0xFFF6F7F9) // 배경(부드러운 연회색 — 순백보다 덜 눈부심)
val CardLight = Color(0xFFFFFFFF) // surfaceContainer(카드가 흰색으로 뜬다)
val CardHighLight = Color(0xFFEFF1F4) // surfaceContainerHigh
val BorderLight = Color(0xFFE5E8EB) // outlineVariant(옅은 테두리)
val OutlineLight = Color(0xFFB4BAC4) // outline
val InkLight = Color(0xFF191F28) // onSurface(차콜 — 순수 검정보다 부드럽다)
val BodyLight = Color(0xFF5B6675) // onSurfaceVariant(본문·캡션)

// ── 무채색: 다크 ──
val CanvasDark = Color(0xFF121318)
val CardDark = Color(0xFF20222A)
val CardHighDark = Color(0xFF2A2C35)
val BorderDark = Color(0xFF34363F)
val OutlineDark = Color(0xFF6B7280)
val InkDark = Color(0xFFE6E8EC)
val BodyDark = Color(0xFFAAB2BD)

// ── 4개 영역 색코딩(리포트·숙달 지도) — 알록달록하되 절제 ──
val AreaNumber = Color(0xFF4C8DF6) // 수와 연산 = 파랑
val AreaChange = Color(0xFF12B26E) // 변화와 관계 = 민트
val AreaShape = Color(0xFFE84C46) // 도형과 측정 = 코랄
val AreaData = Color(0xFFC77D0E) // 자료와 가능성 = 앰버
