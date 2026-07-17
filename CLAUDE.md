# CLAUDE.md — 딱풀(DdakPul) 프로젝트 헌법

**딱풀** — "딱 맞는 문제를 풀다". **전 연령 적응형 사고력 수학 학습 앱.**
문제를 풀면 정답 여부와 누적 실력으로 다음 문제를 자동 추천하고, 학습 리포트를 제공한다.

- **타깃**: 초등부터 성인까지 — 학년이 아니라 **사고력 난이도(1~N, 현재 상한 10)** 한 축.
  1=유아·초등 입문, 상위=경시·올림피아드급. **천장을 한 칸 올릴 때는 그 층을 4개 영역
  (수와연산·변화와관계·도형과측정·자료와가능성) 모두 채운다.**
- **문제 유형**: 연습장 펴고 5분 생각할 다단계 사고력 문제(퍼즐·추론·전략·조합). **계산 드릴 금지.**
- **사용자**: 학습자(아동~성인) + 보호자(리포트). 디바이스: 안드로이드 태블릿 우선(폰 대응).
- 패키지 `com.ddakpul.math` · 리포 github.com/AlgoLovers/ddakpul

## 핵심 원칙 (절대 위반 금지)

1. **런타임 AI 호출 비용 0원** — 추천은 순수 규칙 기반, 온디바이스 완결.
2. **문제는 사전 생성·앱 내장** — 실시간 생성 금지.
3. **오프라인 우선** — 네트워크 없이 핵심 기능 전부 동작.
4. **Domain 계층에 `android.*` import 금지** — 순수 Kotlin (상세: `.claude/rules/domain-purity.md`).
5. 의존성 방향: Presentation/Data → Domain. 역방향 금지.
6. **실행 코드(.so/dex)는 절대 런타임 다운로드 금지**(Play 정책) — 데이터 파일만 허용.
7. **구매 UI는 `Monetization.BILLING_ENABLED`(현재 false) 뒤에** — 결제 미연동 상태에서
   가격·활성화 버튼 노출 금지.

## 기술 스택 · 구조

Kotlin · Jetpack Compose(M3) · Clean Architecture 3계층 + MVVM · Hilt · Room ·
WindowSizeClass 반응형 · minSdk 26 · JDK 17 · Gradle KTS + Version Catalog.

```
app/src/main/java/com/ddakpul/math/
├── core/ (common·designsystem·di)   ├── data/ (local Room·repository·mapper)
├── domain/ (model·repository IF·usecase — 순수 Kotlin ⭐)
└── presentation/ (solve·result·report·home·settings·… + ui/DdakPulApp.kt 내비)
```

도메인 모델(Problem·Attempt·LearnerState 등)은 `domain/model/`이 원전 — 여기 옮겨 적지 않는다.
문제은행: `ProblemCatalog.kt`(수제) + `assets/problems_generated*.json`(생성·한/영, 총 963+).

## 추천 알고리즘 (그룹 단위 추천, 전부 순수 함수 + 단위 테스트)

1. 연속 2정답 → 난이도 +1 그룹 / 2. 연속 2오답 → −1 그룹 / 3. 혼조 → 같은 난이도 유지
4. 정체(같은 난이도 N회 오답 누적) → 대표문제 해설 + 선수 개념 그룹으로
5. 그룹 내에서는 최근에 안 푼 문제 중 랜덤 / 6. `Difficulty.MIN~MAX`로 clamp
7. 재도전: 직전 1문제만 틀렸으면 같은 그룹의 **다른** 문제
8. 간격 복습: 숙달 그룹을 Leitner 박스(1·3·7·14·30일)로, 3문제마다 1복습 슬롯(난이도 불변)

**우선순위: 4(정체) > 8(복습) > 1·2(승급/강등) > 7(재도전) > 3(유지)**
구현: `domain/usecase/RecommendNextProblemUseCase.kt`(+`ComputeReviewQueueUseCase.kt`).
규칙 변경 시 테스트·이 표·`docs/PEDAGOGY.md`(연구 근거)를 함께 갱신.

## 코딩 규칙

- 불변 우선(`val`), `!!` 금지, 매직값 금지(상수/enum), 생성자 주입만.
- ViewModel은 UseCase만 호출(Repository 직접 호출 금지). UI State = 단일 불변 객체 + `StateFlow`.
- Compose에 비즈니스 로직 금지. 성공/실패는 `Result`+`AppError`.
- Git: `main`(배포, PR+CI로만) / `develop`(통합) / `feature/*`.
  Conventional Commits(`feat|fix|refactor|test|docs|chore(scope): 한국어 요약`), 한 커밋 = 한 논리 변경.

## 하네스 (스킬·에이전트·훅·규칙)

- **스킬** `.claude/skills/`: `/wrap-up`(턴 종료 의식) · `/release-aab`(서명 번들, 사용자 호출 전용) ·
  `/emu-qa`(에뮬 스샷 QA 루프) · `/gen-problems`(문제 생성 파이프라인). 반복 절차는 여기에 명문화한다.
- **에이전트** `.claude/agents/`: `problem-auditor`(문제 콘텐츠 감사, 읽기 전용 — 문제 추가·수정 후 필수) ·
  `pedagogy-researcher`(학습과학 리서치 브리프). ⚠️ 에이전트 모델은 opus/sonnet/haiku만 — **fable 금지**(유료 크레딧).
- **훅** (`.claude/settings.json` → `tools/claude/hooks/`): SessionStart가 git fetch+동기화 상태 주입,
  Stop이 더티 트리를 경고. 훅이 알려주는 상태를 무시하지 말 것.
- **경로 규칙** `.claude/rules/`: domain-purity(도메인 순수성) · problemgen(솔버 검증·이중언어 불변식).
- 대량 배치(문제 생산 등)는 진행 상태를 파일로 외재화하고, 솔버 검증이 있는 영역에서만 루프를 돌린다.

## 세션 조율 (터미널 + 텔레그램 상주 세션이 한 리포 공유)

- **턴 끝 = 깨끗한 트리**: `/wrap-up`으로 spotless→detekt→커밋→푸시까지. (미커밋 잔류로 6파일 충돌 전례.)
- 시작 시 SessionStart 훅이 fetch·동기화 상태를 알려준다 — 뒤처졌으면 pull부터.
- **무거운 다중 파일 작업은 한 창구에서.** 두 세션이 동시에 편집해야 하면 한쪽은
  **git worktree로 격리**(`.claude/worktrees/`는 gitignore, 필요한 로컬 파일은 `.worktreeinclude` —
  키스토어는 절대 포함 금지).
- **커밋 금지**: `keystore.properties`, `*.keystore`(업로드 키 — 잃으면 업데이트 불가), `.aab`/`.apk`.
  권한 deny로도 막혀 있음. 백업은 사람이 관리(구글 드라이브, 2026-07 완료).

## 작업 방식

- **수직 슬라이스**(한 기능 관통) 단위로 진행, 단계마다 커밋.
- Domain UseCase는 반드시 단위 테스트 동반 — 특히 추천 규칙 1~8은 규칙별 테스트 필수.
- UI 변경은 `/emu-qa`로 스크린샷 자가 검증 — **라이트/다크 둘 다**(테마 규칙: `docs/DESIGN.md`).
- 새 학습 기능은 `pedagogy-researcher`로 근거 조사 후 설계(근거 대장: `docs/PEDAGOGY.md`).
- 출시·수익화 실무는 `docs/LAUNCH.md`, 방향은 `docs/ROADMAP.md`, 피드백 대장은 `docs/FEEDBACK_LOG.md`.
