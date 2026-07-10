# 딱풀 (DdakPul)

> "딱 맞는 문제를 풀다" — 초등 사고력 수학 적응형 학습 앱

아이가 문제를 풀면 정답 여부와 누적 실력 데이터를 바탕으로 **다음에 풀 문제를 온디바이스에서 자동 추천**한다.
추천은 서버·외부 API 없이 순수 규칙 기반 알고리즘으로 동작하므로 **런타임 비용이 0원**이고, **오프라인**에서 완결된다.

- **타깃**: 초등 사고력 수학 — 학년 구분 없이 난이도 1~5
- **디바이스**: 안드로이드 태블릿 우선(폰 대응)
- **패키지**: `com.ddakpul.math`

## 핵심 흐름

```
홈(오늘의 목표·스트릭) → 문제 풀기 → 채점(해설·오개념·과정 칭찬) → 다음 문제 자동 추천 → 반복
                                                    └ 부모용 리포트(인사이트·차트·숙달도) → 학습지 인쇄(A4 + 정답지)
```

주요 기능:
- **적응형 추천** — 온디바이스 규칙 기반, 연속 정답/오답에 따라 난이도 자동 조절, 정체 감지 시 해설+선수 개념 복귀
- **동기부여** — 오늘의 목표(10문항) 진행바, 관대한 스트릭, 성장 마인드셋 기반 과정 칭찬 메시지
- **학부모 리포트** — 문장형 인사이트, 2주 학습량/정답률 추이/난이도 성장 차트, 개념별 숙달 단계, 부모 가이드 팁
- **인쇄 학습지** — A4 문제지(풀이 공간 포함) + 정답·해설 별지, 오답 위주/추천 출제, 영역 필터

설계의 교육학적 근거는 [`docs/PEDAGOGY.md`](docs/PEDAGOGY.md)에 정리되어 있다.

## 기술 스택

Kotlin · Jetpack Compose(Material 3) · Clean Architecture(3-layer) + MVVM · Hilt · Coroutines/Flow · Room · WindowSizeClass(태블릿 반응형)

- minSdk 26 / compileSdk 36 / JDK 17
- Gradle Kotlin DSL + Version Catalog

## 아키텍처

`presentation` / `data` → `domain` (역방향 금지). `domain`은 순수 Kotlin(`android.*` import 금지).
자세한 규칙은 [`CLAUDE.md`](CLAUDE.md) 참조.

## 추천 알고리즘 (비용 0)

문제는 개별이 아니라 **그룹(유사 개념·난이도 묶음)** 단위로 추천한다. 규칙은
[`RecommendNextProblemUseCase`](app/src/main/java/com/ddakpul/math/domain/usecase/RecommendNextProblemUseCase.kt)
에 순수 함수로 구현되고, 규칙 1~6이 각각 단위 테스트로 검증된다.

1. 연속 2회 정답 → 난이도 +1
2. 연속 2회 오답 → 난이도 −1
3. 혼조(정답·오답 반복) → 같은 난이도 유지
4. 정체 감지(같은 난이도 누적 오답 N회) → 대표문제 해설 제공 + 선수 개념으로 복귀
5. 결정된 그룹 내 최근에 풀지 않은 문제 중 랜덤 출제
6. 난이도는 1~5로 clamp

## 빌드 / 테스트

```bash
./gradlew testDebugUnitTest   # 단위 테스트 (추천 알고리즘 규칙 검증)
./gradlew assembleDebug       # 디버그 APK
./gradlew spotlessApply       # 포맷
./gradlew detekt              # 정적 분석
```

로컬 빌드에는 `local.properties`의 `sdk.dir`(안드로이드 SDK 경로)가 필요하다.
