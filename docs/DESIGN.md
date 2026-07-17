# DESIGN.md — 딱풀 디자인 헌법

> 근거 리서치(M3 색 시스템·Compose 테마 규율·아동 UX·QA 프로세스, 2026-07)와
> **실제 사고**(다크 모드 흰 배경 + 흰 글씨, 갤럭시 탭 전면 발생)에서 도출한 운영 규칙.
> 이 사고의 근본 원인은 색 감각이 아니라 **"루트를 칠하는 책임"과 "다크 검증 단계"가
> 프로세스에 없었던 것** — 그래서 규칙과 검증을 함께 명문화한다.

## 원칙

아동이 **혼자 읽고, 혼자 누를 수 있어야** 한다. 색은 취향이 아니라 **역할(role)** 이고,
모든 화면은 라이트·다크 두 벌이 **동시에** 완성되어야 한다.

## 하드 룰 (위반 = 버그)

1. **색 리터럴 격리** — `Color(0xFF…)`는 `core/designsystem/theme/`에만. 화면 코드는
   오직 `MaterialTheme.colorScheme.*`. (예외: 도형 렌더러처럼 콘텐츠 자체의 색)
2. **짝 규칙** — 배경이 `X`면 그 위 글자·아이콘은 반드시 `onX`. 임의 조합 금지.
   (사고 사례: 옅은 회색 배지 원 위 `Color.White` 글자 → 대비 미달)
3. **루트는 반드시 칠한다** — 화면 최상위는 `Scaffold` 또는 `Surface`. 맨 `Box/Column`
   루트 금지. MainActivity가 루트 Surface로 전 화면을 감싸지만, Dialog·새 창은 각자 책임.
   (사고 사례: 태블릿 레일 분기에 Scaffold 없음 → 흰 창 배경 + 다크 글씨)
4. **두 벌 동시 완성** — 새 색 역할은 light/dark 값이 **같은 커밋**에 들어온다.
   창 테마(`values/themes.xml` ↔ `values-night/themes.xml`)도 짝으로 관리.
5. **대비 숫자** — 본문 4.5:1, 큰 글자·아이콘 3:1 (WCAG AA). 새 색 짝 추가 시 확인.
6. **터치 타겟** — 최소 48dp. 아이가 누르는 핵심 액션(선택지·채점·다음 문제)은 56dp+ 와
   8dp+ 간격.
7. **타이포·간격 토큰만** — `MaterialTheme.typography.*`와 4dp 그리드. 임의 sp/dp 금지.
   fontScale 1.5에서 잘리면 버그.
8. **edge-to-edge** — 상태바 아이콘 대비를 라이트/다크 각각 확인. 인셋은 Scaffold가 소비
   (태블릿 레일 분기는 `systemBarsPadding()` — 기존 인셋 사고 참조).
9. **제조사 강제 다크 차단** — 앱이 다크를 직접 처리하므로 `forceDarkAllowed=false` 유지.

## 현행 팔레트 (역할 → 값)

원전은 `core/designsystem/theme/Color.kt`·`Theme.kt`. 요지:
- 캔버스: 라이트 `EDEBF7`(라벤더 틴트 — 순백 금지, 눈부심) / 다크 `121318`
- 카드(surfaceContainer): 라이트 `FCFBFF`(캔버스 위에 뜨는 밝은 카드) / 다크 `25252C`
- Primary 바이올렛 / Secondary 민트(정답) / Tertiary 앰버(안내·프로모) / Error 레드(오답)
- 공용 카드 모양: 20dp 라운드 + 1dp 그림자 (StatTile·SectionCard)

## QA 매트릭스 (UI 변경 시)

| 축 | 값 |
|---|---|
| 테마 | **light / dark (둘 다 필수)** |
| 기기 | phone / tablet (레이아웃 분기가 다르면 둘 다) |
| 폰트 | 1.0 / (릴리스 전) 1.5 |

- 실행: `/emu-qa` 스킬 — 다크 전환은 `adb shell cmd uimode night yes|no`.
- 핵심 화면: 홈 · 풀이 · 결과 · 리포트 · 설정.
- 릴리스 전: Accessibility Scanner 1회(대비·타겟 크기).

## 디자인 도구 (2026-07 리서치 → 채택/보류)

리서치 2건(디자인 QA 하네스 · 세련된 룩 리소스)에서 도출. AI 에이전트로 Compose 앱을
개발할 때 쓰이는 도구들 중 딱풀(솔로·프리런치)에 맞는 것만 채택.

**적용됨**
- **compose-lints**(slackhq, `lintChecks`) — 모디파이어 재사용·하드코딩 파라미터·불안정 컬렉션 등
  위험 패턴을 Lint에서 잡는 가드레일. `abortOnError=false`로 릴리스는 안 막고 표시만.
- **Pretendard 서체**(OFL) — 실사용 글자만 서브셋(≈0.4MB, `tools/fonts/subset.py`). 콘텐츠 바꾸면 재실행.
- **@Preview** — 디자인 시스템 컴포넌트에 라이트/다크 미리보기(`ComponentPreviews.kt`). Android Studio
  디자인 반복 + 스크린샷 테스트의 전제조건.

**출시 후 도입 후보 (지금은 미적용)**
- **스크린샷 회귀 테스트** — Paparazzi(JVM·CI에 에뮬 불필요) 또는 Google 공식 Compose Preview
  Screenshot Testing. `@Preview`가 이미 있어 붙이면 라이트/다크×폰트스케일이 자동 회귀 테스트가 됨.
  ⚠️ 현재 AGP 8.11이 최신이라 서드파티 플러그인 버전 정합에 주의 — 한 번에 집중해서 붙일 것.
  ComposablePreviewScanner(sergio-sastre)로 프리뷰→테스트 자동 수집 결합이 표준.
- **Compose 접근성 체크** — 테스트에서 `composeTestRule.enableAccessibilityChecks()`(대비·48dp 터치·라벨).
- **M3 Expressive**(셰이프 모핑·스프링 모션) — material3 1.5.0 정식화 후. 지금은 alpha·실험 API라 보류.
- **비주얼 격상**(오너 취향: 3D 클레이·그라데이션·마스코트): 3dicons(CC0)·Fluent 3D 이모지(MIT) 아이콘,
  Lottie(마스코트/정답 축하), Konfetti+햅틱, 네이티브 그라데이션/소프트 섀도우. 되돌리기 쉬운 것부터.
- **제외**: 무거운 서드파티 UI 킷 통째 채택(버전 종속·방치 리스크), Google Relay(2025 종료).

## do / don't 박제 (실사고)

- ❌ 태블릿 레일 `Row`에 배경 없이 화면 배치 → 다크 모드에서 흰 창 배경 노출 (2026-07 실사고)
- ❌ `parent="Theme.Material.Light"` 단독 + values-night 없음 → 창 배경이 항상 흰색
- ✅ 루트 `Surface(color = colorScheme.background)` + values-night 창 테마 짝
- ❌ 배지 원(`outlineVariant`) 위 `Color.White` 글자 → 라이트에서 안 보임
- ✅ 상태별로 짝 색: 옅은 배경이면 `onSurfaceVariant`, 진한 배경이면 White
