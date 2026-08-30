# 아키텍처 — 계층과 경계

딱풀은 **Clean Architecture 3계층 + MVVM**이다. 이 문서는 계층이 무엇을 맡고, 무엇을
알아도 되고, 어떤 규칙이 자동으로 강제되는지를 적는다. 코드에서 확인할 수 있는 사실
(모델 필드, 화면 목록)은 여기 옮겨 적지 않는다 — 원전은 코드다.

관련 문서: 추천 규칙은 `CLAUDE.md`의 규칙 표, 근거는 `PEDAGOGY.md`, 릴리스는 `RELEASE.md`.

## 계층

```
presentation / ui  ──▶  domain  ◀──  data
      core (designsystem · di · common)
```

| 계층 | 맡는 것 | 알아도 되는 것 |
|---|---|---|
| `domain` | 규칙·정책·모델. 추천, 채점, 복습 스케줄, 통계 해석 | **아무것도** — 순수 Kotlin |
| `data` | Room·assets·네트워크로 domain 인터페이스를 구현 | domain |
| `presentation` | 화면 상태와 그리기. UseCase 호출, UI 이벤트 | domain, core |
| `core` | 디자인 시스템, DI 모듈, 프레임워크 유틸 | domain |

의존은 **안쪽으로만** 흐른다. `data`와 `presentation`은 서로를 모른다.

## 절대 규칙 (테스트로 강제됨)

`app/src/test/.../architecture/ArchitectureRulesTest.kt`가 소스 트리를 읽어 검사한다.
어기면 `./gradlew testDebugUnitTest`가 실패한다 — 리뷰를 통과해도 CI가 막는다.

1. **`domain`에 `android.*`·`androidx.*` import 금지.** 순수 Kotlin/JVM만.
2. **`domain`은 `data`·`presentation`·`core`·`ui`를 import하지 않는다.**
   그래서 `AppResult`·`AppError`·`MILLIS_PER_DAY`·`toPercentInt`는 `core.common`이 아니라
   `domain/common`에 있다 — 예전엔 core에 있어서, 그 패키지에 프레임워크 코드가 하나만
   추가되면 도메인 순수성이 조용히 깨질 수 있었다.
3. **화면(`presentation`·`ui`·`core.designsystem`)은 `data`를 import하지 않는다.**
4. **ViewModel은 Repository를 직접 주입받지 않는다.** UseCase만 호출한다.
5. **`!!` 금지.**

detekt의 `ForbiddenImport`는 프로젝트 전체에 같은 규칙을 걸어 "domain에서만 금지" 같은
경로별 규칙을 만들 수 없다. 그래서 규칙 검사는 테스트로 구현했다(추가 의존성 없음).

## 시간은 주입한다 — `Clock`

`System.currentTimeMillis()`·`TimeZone.getDefault()`를 **직접 부르는 곳은 `SystemClock`
하나뿐이다.** 나머지는 `domain/time/Clock`을 주입받는다.

```kotlin
interface Clock {
    fun nowMillis(): Long
    fun zoneOffsetMillis(): Long
}
```

이유는 테스트다. 시계를 직접 부르면 "문항을 30분 넘게 열어둔 채 기기가 잠든" 상황을
검증할 방법이 없어, 시간이 얽힌 코드 전체가 테스트 밖에 남는다. 실제로 이 프로젝트의
ViewModel 테스트는 0개였고, `Clock` 도입 직후 작성한 첫 테스트가 **첫 제출 뒤 모든
제출이 막히던 버그**(v1.0.0에 포함되어 출시)를 잡아냈다.

- 화면·저장소: 생성자로 `Clock`을 받는다.
- UseCase: 시간을 **파라미터로** 받는다(`nowMillis`, `zoneOffsetMillis`). 순수 함수로
  남기기 위해서다 — UseCase가 `Clock`을 들면 순수성이 흐려진다. 시각을 정하는 것은
  호출부(ViewModel)의 몫이다.
- 테스트: `FakeClock`으로 시간을 원하는 만큼 앞으로 돌린다.

## Repository는 관심사 단위로 자른다

| 인터페이스 | 맡는 것 |
|---|---|
| `LearnerRepository` | 학습 **기록** — 시도, 현재 난이도, 진도 초기화 |
| `LearnerPreferencesRepository` | 사람이 고른 **설정** — 하루 목표, 상위 난이도 열기 |
| `ProblemRepository` | 문제은행(시딩·조회) |
| `ProblemFeedbackRepository` | "별로예요" 제외 목록 |
| `OnboardingRepository` | 첫 실행 온보딩 상태 |
| `SolutionVideoRepository` | 해설 영상 매니페스트·캐시 |

기록과 설정을 나눈 이유는 수명이 다르기 때문이다 — **진도를 초기화해도 하루 목표는
남는다.** 예전엔 한 인터페이스가 둘을 모두 담아 11개 메서드로 부풀었고, 설정만 필요한
화면까지 풀이 기록 API를 함께 들고 다녔다.

### 단일 행을 나눠 쓸 때: 필드별 UPDATE

`learner_progress`는 한 행에 난이도·하루 목표·온보딩·설정이 함께 있다. 저장은 반드시
**필드별 `UPDATE`**로 한다(`LearnerProgressDao`). 행 전체를 읽고-고쳐-다시 쓰면, 문제를
넘길 때마다 자동 저장되는 난이도와 사용자가 바꾼 하루 목표가 서로를 덮어쓴다.

## UseCase 규약

- 단일 책임, `operator fun invoke` 하나만 노출, 생성자 주입만.
- 성공/실패는 예외가 아니라 `AppResult` + `AppError`.
- UseCase가 UseCase를 부르는 것은 정상이다(`SubmitAnswerUseCase` → `GradeAttemptUseCase`,
  `RecordAttemptUseCase`).
- **도메인 불변식은 도메인이 보증한다.** 예: 시도 기록 시간 상한은
  `RecordAttemptUseCase`가 clamp한다 — 화면에 맡기면 새 풀이 경로가 생길 때 빠진다.
- 추가·수정하면 단위 테스트 동반 필수.

## ViewModel 규약

- UseCase만 호출한다(테스트로 강제).
- UI 상태는 **단일 불변 객체 + `StateFlow`**.
- 해석·판정은 domain에서 한다. ViewModel은 스트림을 합쳐 상태로 옮기는 일만 한다 —
  "어떤 인사이트를 언제 띄우는지"(연속일 기준, 정답률 변화 임계폭, 취약 개념 판정선)는
  교육 정책이므로 `BuildLearningReportUseCase`에 있다.
- 시간은 `Clock`으로 받는다.

## Compose 규약

- 비즈니스 로직 금지. 상태는 **호이스팅**한다 — 컴포저블에 ViewModel을 통째로 넘기지
  말고 값과 콜백을 넘긴다(미리보기·재사용 가능).
- 화면 파일이 긴 것 자체는 문제가 아니다(선언형이라 자연스럽다). 함수 하나가 커지는 것을
  본다.

## 아직 남은 것

- `WorksheetPdfGenerator`(787줄)·`ReportScreen`(799줄)은 파일 분리 여지가 있다. 함수
  단위는 작아 시급하지 않다.
- `LearningStats` 집계는 전체 시도를 여러 번 순회한다. 기록이 수천 건으로 늘면 한 번의
  순회로 접는 것을 검토한다(현재는 `Dispatchers.Default` + `conflate`로 충분).
