# CLAUDE.md — 딱풀(DdakPul) 프로젝트 규칙

> 이 파일은 프로젝트 루트에 위치하며, Claude Code가 항상 참조하는 프로젝트 헌법이다.

## 프로젝트 정체성

**딱풀 (DdakPul)** — "딱 맞는 문제를 풀다"

**전 연령 적응형 사고력 수학 학습 앱.** 문제를 풀면 정답 여부와 누적 실력 데이터를 바탕으로 다음에 풀 문제를 자동 추천한다. 학습 리포트를 제공한다.

- **타깃**: **초등부터 성인까지 — 학년이 아니라 '사고력 난이도 폭'(1~N) 한 축으로 이어진다.** 1은 유아·초등 입문, 상위는 중·고·경시·대학·올림피아드급. 엔진(사고력＋적응형＋통계)은 학년을 가리지 않으므로, **천장(`Difficulty.MAX`)을 차근차근 올리고 상위 콘텐츠를 채워** 확장한다(현재 상한 10). 시작은 초등에서 했지만 지향은 전 연령. **천장을 한 칸 올릴 때는 그 층을 4개 영역(수와연산·변화와관계·도형과측정·자료와가능성) 모두 채워 균형을 맞춘다.**
- **문제 유형**: 연습장이 필요한 다단계 사고력 문제(퍼즐·추론·전략·정수론·조합·게임). 계산 드릴 금지 — 계산은 사고의 도구일 뿐
- **사용자**: 학습자(문제 풀이) — 아동부터 성인까지. 아동은 보호자가 리포트로 지켜본다(연령대별 카피는 점진적으로 중립화)
- **디바이스**: 안드로이드 태블릿 우선 (폰도 대응)
- **패키지명**: `com.ddakpul.math`

## 핵심 원칙 (절대 위반 금지)

1. **런타임 AI 호출 비용은 0원이다.** 문제 추천은 순수 규칙 기반 알고리즘으로 동작한다. 서버·외부 API 호출 없이 온디바이스에서 완결된다.
2. **문제 데이터는 앱에 내장(사전 생성)된다.** 실시간 문제 생성 금지.
3. **오프라인 우선.** 네트워크 없이 모든 핵심 기능이 동작해야 한다.
4. **Domain 계층에 `android.*` import 금지.** 순수 Kotlin만.
5. 의존성 방향: Presentation/Data → Domain. 역방향 절대 금지.

## 기술 스택

- Kotlin, Jetpack Compose (Material 3)
- Clean Architecture (3-layer) + MVVM
- Hilt (DI), Coroutines/Flow
- Room (로컬 DB) — 문제은행 및 학습기록 저장
- 태블릿 대응 반응형 레이아웃 (WindowSizeClass)
- minSdk 26, JDK 17, Gradle Kotlin DSL + Version Catalog

## 아키텍처

```
com.ddakpul.math
├── core/
│   ├── common/          # Result, AppError, 확장함수, 상수
│   ├── designsystem/    # Compose 테마, 공통 컴포넌트
│   └── di/              # Hilt 모듈
├── domain/              # ⭐ 순수 Kotlin (android 의존성 금지)
│   ├── model/           # Problem, Attempt, ConceptTag, Difficulty, LearnerState...
│   ├── repository/      # 인터페이스만
│   └── usecase/         # 단일 책임 UseCase
├── data/
│   ├── local/           # Room DB, DAO, Entity, 초기 문제 시딩
│   ├── repository/      # RepositoryImpl
│   └── mapper/
└── presentation/
    ├── solve/           # 문제 풀이 화면 (핵심)
    ├── result/          # 정답/해설 화면
    ├── report/          # 부모용 리포트
    ├── home/
    └── settings/
```

## 도메인 모델 (핵심 개념)

```kotlin
// 문제
data class Problem(
    val id: String,
    val area: MathArea,          // 수와연산 / 변화와관계 / 도형과측정 / 자료와가능성
    val conceptTags: List<String>,
    val difficulty: Int,         // 1~N (Difficulty.MIN..MAX, 천장은 점진 확장)
    val groupId: String,         // 유사 난이도·개념 묶음 (추천 단위)
    val statement: String,
    val answer: Answer,
    val explanation: String?,    // 모든 문제가 단계별 풀이 보유 (콘텐츠 규칙)
    val commonMistakes: List<Mistake>,
)

// 풀이 시도 기록
data class Attempt(
    val problemId: String,
    val isCorrect: Boolean,
    val timeSpentSec: Int,
    val timestamp: Long,
)

// 학습자 상태 (추천의 입력)
data class LearnerState(
    val currentDifficulty: Int,              // 현재 난이도
    val areaMastery: Map<MathArea, Float>,   // 영역별 숙달도
    val recentAttempts: List<Attempt>,
)
```

## 추천 알고리즘 규칙 (비용 0, 순수 로직)

문제는 **개별 문제가 아니라 그룹(유사 개념·난이도 묶음)** 단위로 추천한다.

1. **정답 시**: 연속 2회 정답 → 난이도 +1 그룹으로 이동
2. **오답 시**: 연속 2회 오답 → 난이도 −1 그룹으로 이동
3. **혼조 시**(맞았다 틀렸다 반복): 같은 난이도 그룹에서 계속 출제 (숙달 미완)
4. **정체 감지**: 같은 난이도에서 N회 이상 오답 누적 → 해당 개념의 **대표문제 해설 제공** + 선수 개념 그룹으로 되돌리기
5. **문제 선택**: 결정된 그룹 내에서 **최근에 풀지 않은 문제 중 랜덤**
6. 난이도 하한/상한은 `Difficulty.MIN`~`MAX`로 고정 (clamp) — 천장은 전 연령 확장 위해 점진 상향
7. **오답 재도전** (v0.3): 직전 한 문제만 틀렸으면(혼조 유지 상황) 같은 그룹의 **다른** 문제를 재도전으로 출제 — 교정 직후 성공 경험
8. **간격 복습** (v0.3): 숙달(연속 2정답)한 그룹을 Leitner 박스(1·3·7·14·30일)로 추적, 만기 그룹이 있으면 **오늘 3문제마다 1문제를 복습 슬롯**으로 배정. 복습은 현재 난이도를 바꾸지 않는다

우선순위: 정체 처치(4) > 복습(8) > 승급/강등(1·2) > 재도전(7) > 유지(3)

> 이 로직은 전부 `domain/usecase/RecommendNextProblemUseCase.kt`(+ `ComputeReviewQueueUseCase.kt`)에 순수 함수로 구현하고, 단위 테스트로 각 규칙을 검증한다. 각 규칙의 연구 근거는 `docs/PEDAGOGY.md`.

## 코딩 규칙

- 불변 우선(`val`), `!!` 금지, 매직값 금지(상수/enum)
- UseCase = 단일 책임, `operator fun invoke` 하나만 노출
- ViewModel은 UseCase만 호출 (Repository 직접 호출 금지)
- 성공/실패는 `Result` + `AppError`로. 예외를 흐름 제어에 쓰지 않음
- UI State는 단일 불변 객체 + `StateFlow`
- Compose에서 비즈니스 로직 금지
- 생성자 주입만 사용

## Git 규칙

- 브랜치: `main`(배포) / `develop`(통합) / `feature/*`
- Conventional Commits: `feat(solve): 문제 풀이 화면 구현`
- 타입: `feat` `fix` `refactor` `test` `docs` `chore`
- 한 커밋 = 한 논리적 변경

## 세션 조율 (⚠️ 중요 — 창구가 둘이다)

이 프로젝트는 **두 개의 Claude 세션**이 같은 저장소를 공유한다: (1) 터미널 세션, (2) 텔레그램 봇
상주 세션(`com.user.claudetelegram-ddakpul`). 둘은 대화를 공유하지 않으므로 아래 규약을 **양쪽 다** 지킨다.

- **작업 끝에 트리를 항상 깨끗이 남긴다.** 한 턴을 마칠 때 `spotlessApply` → `detekt` → 커밋까지
  끝낸다. 미커밋 파일을 남기면 다른 세션이 물려받아 충돌한다(실제로 6파일 충돌 발생함).
- **시작 전 `git fetch` + 최신 develop 반영.** 양쪽이 같은 원격에 푸시하므로 시작 시 동기화한다.
- **무거운 다중 파일 작업은 한 창구에서.** 큰 기능 개발 중이면 다른 창구는 조회·상태확인·소규모 수정만.
- **빌드 산출물·비밀은 절대 커밋 금지:** `keystore.properties`, `ddakpul-upload.keystore`(업로드 키),
  `.aab`/`.apk`. 업로드 키를 잃으면 앱 업데이트가 곤란하니 별도 백업은 사람이 관리한다.

## 테스트

- Domain UseCase는 **반드시** 단위 테스트 동반 (특히 추천 알고리즘)
- 추천 알고리즘은 위 규칙 1~6을 각각 검증하는 테스트 케이스 필수

## 작업 방식

- 큰 요청 대신 **수직 슬라이스(한 기능 관통)** 단위로 진행
- 최우선 목표: **문제 1개 풀기 → 채점 → 다음 문제 추천**의 한 바퀴 관통
- 각 단계 완료 시 커밋
